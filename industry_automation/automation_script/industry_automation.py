import zipfile
import os
import tempfile
import requests
import logging
import socket
import shutil
import argparse

from pathlib import Path
import re
from ast import literal_eval
from lxml import etree

# Setup logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

 # Map DB version to fixed port
VERSION_PORT_MAP = {
    'saas~18.1': 10001,
    'saas~18.2': 10002,
}
BASE_URL = "http://localhost:"
LOGIN = "admin"
PASSWORD = "admin"

# ====================================================
#              Export logic             
# ====================================================

class ProcessDb:
    def __init__(self, module_name, db_version, category, dump_path, destination_path, master_password):
        self.module_name = module_name
        self.db_version = db_version
        self.category = category
        self.dump_path = dump_path
        self.destination_path = destination_path
        self.master_password = master_password

    def process_dump_task(self):
        try:
            # Extract industry name from the zip filename
            industry_name = self.dump_path.split('/')[-1].split('.')[0]

            # 2. Get the DB version (first two parts of semantic versioning, e.g., 16.0)
            port = self.get_port_for_version()

            # Check if the appropriate Odoo server is running on the correct port
            if not self.is_port_open("localhost" , port):
                _logger.error(f"No server is running on port {port} for DB version {self.db_version}.")
                raise Exception(f"No server is running on port {port} for DB version {self.db_version}.")
            _logger.info(f"Server found on port {port} for DB version {self.db_version}.")

            # 3. Restore the DB using the dump file on the found port
            restore_db_name = f"{self.module_name}_db"
            success = self.restore_db(port, restore_db_name)
            if not success:
                _logger.error(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
                raise Exception(f"Database '{restore_db_name}' Failed to restore  on port {port}.")
            _logger.info(f"Database '{restore_db_name}' restored successfully on port {port}.")

            # 5. Prepare a temporary base directory for exporting and modifying files
            base_temp_dir = os.path.join(tempfile.gettempdir(), industry_name)
            os.makedirs(base_temp_dir, exist_ok=True)

            # 6. Export the Studio customizations into a zip file
            studio_zip_path = f"{base_temp_dir}/studio_customization.zip"
            self.export_studio_customizations(port, restore_db_name, studio_zip_path)

            # 7. Extract the studio zip for cleaning up
            with zipfile.ZipFile(studio_zip_path, "r") as zip_ref:
                zip_ref.extractall(base_temp_dir)

            # 8. Run the external cleanup script to refactor the module
            studio_extract_path = f"{base_temp_dir}/studio_customization"

            try:
                clean_module(self.module_name, self.category, restore_db_name, studio_extract_path, port, self.destination_path)
                _logger.info("Module Clean Up successful")
            except Exception as e:
                raise Exception("Error while Running CleanUp Script", str(e))
            
            # delete temp directory
            self.delete_temp_dir(base_temp_dir)

            # drop restore DB
            self.drop_db(restore_db_name, port)

            
        except Exception as e:
           raise Exception(str(e))
  
    def get_port_for_version(self):
        # Look up the port number mapped to the given DB version
        port = VERSION_PORT_MAP.get(self.db_version)

        # Raise an error if no port is found for the version
        if not port:
            _logger.error(f"No port mapped for DB version {self.db_version}")
            raise Exception(f"No port mapped for DB version {self.db_version}")
        return port
    
    def is_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a TCP port is open on the given host."""
        
        # Create a TCP socket using IPv4
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Set the timeout for the connection attempt
            sock.settimeout(timeout)
            try:
                # Attempt to connect to the specified host and port
                sock.connect((host, port))
                return True
            except (socket.timeout, ConnectionRefusedError):
                # Return False if the connection times out or is refused
                return False

    def restore_db(self, port, db_name):
        """
        Restores the database from the given ZIP file to the Odoo server running on the specified port.

        Args:
            port (int): The port number of the Odoo server where the DB should be restored.
            db_name (str): The name to assign to the restored database.
            temp_zip_file_path (str): Path to the ZIP file containing the DB dump.

        Returns:
            bool: True if the database is restored and credentials are reset, False otherwise.
        """
        try:
            # Open the ZIP file containing the database dump
            with open(self.dump_path, 'rb') as backup_file:
                # Send POST request to Odoo's database restore endpoint
                response = requests.post(
                    f'{BASE_URL}{port}/web/database/restore',
                    data={
                        'master_pwd': self.master_password,  # Master admin password
                        'name': db_name,                # Target DB name
                        'copy': True                    # Indicate it's a copy
                    },
                    files={
                        'backup_file': ('tattoo.zip', backup_file, 'application/zip')
                    }
                )

            # Check if the restore was successful (HTTP 200 OK or 302 Found)
            if response.status_code in (200, 302):
                # Reset login credentials for user ID 2
                os.system(f"psql {db_name} -c \"UPDATE res_users SET login='{LOGIN}', password='{PASSWORD}' WHERE id=2;\"")
                return True
            else:
                return False

        except Exception:
            raise Exception("Database Can't be Restore")

    def drop_db(self, db_name, port):
        response = requests.post(
            f'{BASE_URL}{port}/web/database/drop',
            data={
                'master_pwd': self.master_password,  # Master admin password
                'name': db_name,
            },
        )
        response.raise_for_status()

    def export_studio_customizations(self, port, db_name, studio_zip_path):
        try:
            session = requests.Session()
            # Step 1: Authenticate via /web/session/authenticate (sets session cookie)
            auth_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "db": db_name,
                    "login": LOGIN,
                    "password": PASSWORD,
                },
                "id": 1
            }
            response = session.post(f"{BASE_URL}{port}/web/session/authenticate", json=auth_payload)
            response.raise_for_status()

            # Parse login result
            result = response.json().get("result")
            if not result or not result.get("uid"):
                _logger.error("Authentication Failed")
                raise Exception("Login failed.")
            uid = result["uid"]
            _logger.info("Authentication Successful")
            
            # Step 2: Ensure web_studio is installed
            modules = self.check_web_studio_installed(port, db_name, uid)
            if modules:
                state = modules[0]['state']
                model_id = modules[0]['id']
                if state == "uninstalled":
                    self.install_web_studio(port, db_name, uid, model_id)
            else:
                _logger.error("web_studio module not found in registry.")
                raise Exception("web_studio module not found in registry.")

            # Step 3: Call action_preset on studio.export.model
            preset_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        db_name,
                        uid,
                        PASSWORD,
                        "studio.export.model",
                        "action_preset",
                        [{}],
                    ]
                },
                "id": 2
            }
            preset_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=preset_payload)
            preset_resp.raise_for_status()

            # Step 4: Create export wizard via RPC
            wizard_payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                                db_name,
                                uid,
                                PASSWORD,
                                "studio.export.wizard",
                                "create",
                                [{
                                    "include_additional_data": True,
                                    "include_demo_data": True
                                }]
                            ]
                },
                "id": 3
            }

            wizard_resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=wizard_payload)
            
            wizard_resp.raise_for_status()
            
            if not wizard_resp.json()["result"]:
                _logger.error("Export Wizard Failed to Create")
                raise Exception("wizard id not found")
            wizard_id = wizard_resp.json()["result"]

            # Step 5: Call the export route (no token needed, session is authenticated)
            export_url = f"{BASE_URL}{port}/web_studio/export?active_id={wizard_id}&token=dummytoken"
            export_resp = session.get(export_url, stream=True)
            

            if export_resp.status_code == 200 and export_resp.headers['Content-Type'] == 'application/zip':
                with open(studio_zip_path, "wb") as f:
                    f.write(export_resp.content)
            else:
                _logger.error(f" Export failed: {export_resp.status_code} - {export_resp.text}")
                raise Exception(f" Export failed: {export_resp.status_code} - {export_resp.text}")
            
        except Exception as e:
            _logger.error("studio_customization Failed to Export")
            raise Exception(str(e))
    
    def delete_temp_dir(self, dir_path):
        """
        Deletes a temporary directory and all its contents.
        
        :param dir_path: Full path to the directory.
        """
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)

    def check_web_studio_installed(self, port, db_name, uid):
        # Prepare the JSON-RPC payload to search for the 'web_studio' module
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "search_read",
                    [[["name", "=", "web_studio"]]],
                    {"fields": ["state"], "limit": 1}
                ]
            },
            "id": 2
        }

        # Send the request to the server and parse the JSON response
        response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()
        
        # Return the list of matched module(s) with their state
        if response["result"]:
            return response["result"]
        

    def install_web_studio(self, port, db_name, uid, module_id):
        # Prepare JSON-RPC payload to install the module using button_immediate_install
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "button_immediate_install",
                    [module_id]
                ]
            },
            "id": 4
        }

        # Send request to install the module
        install_response = requests.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()

        # Log error if installation failed
        if not install_response["result"]:
            _logger.error("Module Studio can't install")
        return install_response["result"]



# ====================================================
#              CleanUp logic             
# ====================================================

automated = {
    'author': 'Odoo S.A.',
    'category': '',
    'images': ['images/main.png'],
    'license': 'OPL-1',
    'version': '1.0',
}

mandatory_files = {
    "/static/src/js/my_tour.js": """import {{ _t }} from "@web/core/l10n/translation";
import {{ registry }} from "@web/core/registry";

registry.category("web_tour.tours").add("{ind_name}_knowledge_tour", {{
    url: "/odoo",
    steps: () => [
        {{
            trigger: '.o_app[data-menu-xmlid="knowledge.knowledge_menu_root"]',
            content: _t("Get on track and explore our recommendations for your Odoo usage here!"),
            run: "click",
        }},
    ],
}});
""",
    "/data/mail_message.xml": """<?xml version='1.0' encoding='UTF-8'?>
<odoo noupdate="1">
    <record model="mail.message" id="notification_knowledge">
        <field name="model">discuss.channel</field>
        <field name="res_id" ref="mail.channel_all_employees"/>
        <field name="message_type">email</field>
        <field name="author_id" ref="base.partner_root"/>
        <field name="subtype_id" ref="mail.mt_comment"/>
        <field name="subject">🚀 Get started with Odoo {Ind_name} Shop</field>
        <field name="body" model="knowledge.article" eval="
            '&lt;span>&#x1F44B; Hi! Follow this &lt;a href=\\''
             + obj().env.ref('{ind_name}.welcome_article').article_url 
             + '\\'>onboarding guide&lt;/a>. You can find it anytime in the Knowledge app.&lt;/span>'"/>
    </record>
</odoo>
""",
    "/data/knowledge_article_favorite.xml": """<?xml version='1.0' encoding='UTF-8'?>
<odoo noupdate="1">
    <record id="knowledge_favorite" model="knowledge.article.favorite">
        <field name="article_id" ref="welcome_article"/>
        <field name="user_id" ref="base.user_admin"/>
    </record>
</odoo>
""",
    "/data/knowledge_tour.xml": """<?xml version="1.0" encoding="UTF-8"?>
<odoo noupdate="1">
    <record id="knowledge_tour" model="web_tour.tour">
        <field name="name">{ind_name}_knowledge_tour</field>
        <field name="sequence">2</field>
        <field name="rainbow_man_message">Welcome! Happy exploring.</field>
    </record>
</odoo>
""",
}

def session_authentication(db_name, port):
    session = requests.Session()
    # Step 1: Authenticate via /web/session/authenticate (sets session cookie)
    auth_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": db_name,
            "login": LOGIN,
            "password": PASSWORD,
        },
        "id": 1
    }
    response = session.post(f"{BASE_URL}{port}/web/session/authenticate", json=auth_payload)
    response.raise_for_status()
    result = response.json().get("result")
    if not result or not result.get("uid"):
        raise Exception("Login failed in script.")
    return session, result['uid']

def get_fields_info(db_name, port):

    session, uid = session_authentication(db_name, port)

    payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name,
                    uid,
                    PASSWORD,
                    "ir.model.fields",
                    "search_read",
                    [[]],
                    {
                        "fields": ["model","name", "store", "readonly"]
                    }
                ]
            },
            "id": 1
            }

    resp = session.post(f"{BASE_URL}{port}/jsonrpc", json=payload)
    resp.raise_for_status()
    if not resp.json()["result"]:
        raise Exception("Error in getting model and field name")
    

    return resp.json()["result"]

def get_etree_content(file_path):
    try:
        # Read the xml file and convert into etree content
        content = file_path.read_text(encoding='utf-8')
        etree_content = etree.fromstring(content.encode("utf-8"))
        return etree_content
    except Exception as e:
        raise Exception(f"Error while getting etree content of file ({file_path}): {e}")

def write_etree_content(file_path, etree_content):
    try:
        # Get etree content and convert to xml and write back to file
        content = etree.tostring(etree_content, pretty_print = True, encoding="UTF-8", xml_declaration = True).decode("utf-8")
        file_path.write_text(content, encoding="utf-8")
        return
    except Exception as e:
        raise Exception(f"Error while writing etree content to file ({file_path}): {e}")

def edit_xml_content(ind_name, content):
    # Replacing studio_customization to new module name
    env_ref = re.compile("(env\.ref\('studio_customization\.)(.*)'")
    content = env_ref.sub(lambda m: f"env.ref('{ind_name}.{m.group(2)}'", content)
    # Replacing x_studio_ to x_
    x_studio = re.compile("x_studio_")
    content = x_studio.sub('x_', content)
    # Remove context={'studio': True}
    context_studio = re.compile(" context=\"{'studio': True}\"")
    content = context_studio.sub('', content)
    # Remove studio_customization.
    studio_mod = re.compile("studio_customization\.")
    content = studio_mod.sub('', content)
    # Replace studio_customization/ with industry_name/
    studio_link = re.compile("studio_customization/")
    content = studio_link.sub(ind_name + '/', content)
    # Remove forcecreate="1" if id start with base_module.
    pattern_base_module_forcecreate = re.compile(r'(<record\s+[^>]*id="base_module\.[^"]*"[^>]*?")\s+forcecreate="1"')
    content = pattern_base_module_forcecreate.sub(r"\1", content)
    # Remove base_module.
    pattern_base_module = re.compile(r"base_module.")
    content = pattern_base_module.sub("", content)
    # Replace res_users_ with base.user_admin
    pattern_res_users_7_res_partner = re.compile("res_users_\w+")
    content = pattern_res_users_7_res_partner.sub("base.user_admin", content)
    # Add industry name in ir_ui_view function
    pattern_ir_ui_view = re.compile(r"obj\(\)\.env\.ref\(\'ir_ui_view_")
    content = pattern_ir_ui_view.sub(f"obj().env.ref('{ind_name}.ir_ui_view_", content)
    # Change key of website.webpage with industry_name.homepage
    pattern_ir_ui_view_key = re.compile(r'(<field name="key">)website.homepage(</field>)')
    content = pattern_ir_ui_view_key.sub(rf'\1{ind_name}.homepage\2', content)
    # Replace sub-domain with indutry related sub-domain
    pattern_href_url = re.compile(r'https://(?!www\.)([^/]+)\.odoo\.com')
    content = pattern_href_url.sub(f'https://{ind_name.replace("_", "-")}.odoo.com', content)
    # If web url contain domain then remove
    pattern_url = re.compile(r'(<field name="url">)https://[^/]+(.*?</field>)')
    content = pattern_url.sub(r'\1\2', content)
    # Remove field that have ref uom.
    pattern_product_uom_unit = re.compile(r'\s*<field[^>]*ref="uom.[^"]*"[^>]*\s*/>')
    content = pattern_product_uom_unit.sub('', content)
    
    return content

def remove_computed_fields(fields_info_list, model_name, record, content):
    # Get fields details related to particular model
    model_fields_info = list(filter(lambda x: x.get("model") == model_name, fields_info_list))

    fields_set_in_record = {
        field.get('name') for field in record.xpath('.//field')
    }
    # Remove regular and self closing field if field have store false and readonly is true
    for field_name in fields_set_in_record:
        field_obj = None
        for field_info in model_fields_info:
            if field_info["name"] == field_name:
                field_obj = field_info

        if field_obj and (not field_obj["store"] and field_obj["readonly"]):

            pattern_standard = re.compile(
                rf'\s*<field name="{field_name}">.*?</field>',
                )
            pattern_self_closing = re.compile(
                    rf'\s*<field name="{field_name}"[^>]*\s*/>'
                )
            content = pattern_standard.sub('', content)
            content = pattern_self_closing.sub('', content)

    return content

def remove_unwanted_fields(content, unwanted_fields):
    # Remove field base on list pass
    for unwanted_field in unwanted_fields:
        pattern_regular = rf'\s*<field name="{unwanted_field}">.*?</field>'
        pattern_self_closing = rf'\s*<field name="{unwanted_field}"[^>]*\s*/>'

        content = re.sub(pattern_regular, "", content, flags=re.DOTALL)
        content = re.sub(pattern_self_closing, "", content)

    return content

def remove_model_based_fields(model_name, content):
    # remove some fields based on model
    unwanted_field_of_model = []
    if model_name == 'sale.order.line':
        unwanted_field_of_model = ['technical_price_unit', 'name']
    elif model_name == 'sale.order.template':
        unwanted_field_of_model = ['prepayment_percent']
    elif model_name == 'sign.item':
        unwanted_field_of_model = ['transaction_id']
    elif model_name == 'pos.session':
        unwanted_field_of_model = ['name', 'start', 'stop']
    elif model_name == 'sale.order':
        unwanted_field_of_model = ['date_order', 'prepayment_percent', 'delivery_status', 'amount_unpaid']
    elif model_name == 'pos.config':
        unwanted_field_of_model = ['last_data_change']
    elif model_name == 'crm.lead':
        unwanted_field_of_model = ['email_from', 'company_id', 'country_id', 'city', 'street', 'partner_name', 'contact_name', 'zip', 'reveal_id']
    elif model_name == 'pos.order':
        unwanted_field_of_model = ['date_order', 'state', 'last_order_preparation_change', 'pos_reference']
    elif model_name == 'res.partner':
        unwanted_field_of_model = ['supplier_rank']
    elif model_name == 'purchase.order':
        unwanted_field_of_model = ['date_order', 'date_approve', 'state', 'date_planned']
    elif model_name == 'product.pricelist.item':
        unwanted_field_of_model = ['date_start', 'date_end']
    elif model_name == 'purchase.order.line':
        unwanted_field_of_model = ['date_planned']
    content = remove_unwanted_fields(content, unwanted_field_of_model)

    return content

def unorder_manifest_demo_files(manifest_demo_file_list, current_dir, file_name, ref_name_list, record):
    """
    Ordering manifest demo files
    if record id found in manifest_demo_file_list's ref_name
        then insert new dictionary in before that found element
    else insert at last
    if there is no ref_name simply insert at first location
    """
    if current_dir.endswith('/demo/'):
        manifest_demo_file_dict = {}
        manifest_demo_file_dict['file_name'] = file_name

        manifest_demo_file_dict['ref_name'] = ref_name_list

        file_record_id = record.get('id')
        if manifest_demo_file_dict['ref_name']:
            inserted = False
            for idx, existing in enumerate(manifest_demo_file_list):
                if file_record_id in existing['ref_name']:
                    manifest_demo_file_list.insert(idx, manifest_demo_file_dict)
                    inserted = True
                    break
            if not inserted:
                manifest_demo_file_list.append(manifest_demo_file_dict)
        else:
            manifest_demo_file_list.insert(0, manifest_demo_file_dict)
    return

def arrange_demo_files(destination_module_path, ind_name, manifest_demo_file_list):
    try:
        old_file = Path(destination_module_path + "/demo/ir_ui_view.xml")
        new_file = Path(destination_module_path + "/demo/website_view.xml")
        os.rename(old_file, new_file)
    except Exception as e:
        raise Exception(f"Error while renaming file: {e}")
    # Remove duplicate record from manifest_demo_file_list, first occurance will be stored
    new_manifest_demo_file_list = []
    for file_list in manifest_demo_file_list:
        if file_list['file_name'] == "ir_ui_view.xml":
            file_list['file_name'] = "website_view.xml"
        if file_list['file_name'] not in new_manifest_demo_file_list:
            new_manifest_demo_file_list.append(file_list['file_name'])
    # Added prefic demo/
    unique_manifest_demo_file_list = [ 'demo/' + file_name for file_name in new_manifest_demo_file_list ]

    try:
        manifest_path = Path(destination_module_path + '/__manifest__.py')
        manifest = literal_eval(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise Exception(f"Unable to read manifest file: {e}")
    # Replace manifest demo files with new list, as we read manifest file with literal_eval
    manifest['demo'] = unique_manifest_demo_file_list
    lines = ["{"]
    for key, value in manifest.items():
        if isinstance(value, str):
            lines.append(f"    '{key}': '{value}',")
        elif isinstance(value, list):
            lines.append(f"    '{key}': [")
            for item in value:
                lines.append(f"        '{item}',")
            lines.append("    ],")
        else:
            lines.append(f"    '{key}': {value},")

    lines.append((f"""    'assets': {{
            'web.assets_backend': [
                '{ind_name}/static/src/js/my_tour.js',
            ],
        }},
    'cloc_exclude': [
        'data/knowledge_article.xml',
        'static/src/js/my_tour.js',
    ],
    'images': [
        'images/main.png',
    ],"""))

    lines.append("}")

    # Join lines and write to file
    formatted_manifest = "\n".join(lines)
    try:
        manifest_path.write_text(formatted_manifest, encoding="utf-8")
    except Exception as e:
        raise Exception(f"Unable to write manifest file: {e}")

    return

def write_scss_function(destination_module_path, scss_content_list):
    # Convert the content of scss files to functions and write function website_theme_apply.xml file
    if scss_content_list:
        target_path = Path(destination_module_path + '/demo/' + 'website_theme_apply.xml')
        target_path.parent.mkdir(parents=True, exist_ok=True)
        new_function = ""
        for item in scss_content_list:
            new_function += f"""
    <function model="web_editor.assets" name="make_scss_customization">
        <value eval="{item['url']}" />
        <value eval="{{'
                {item['inner_scss_content']}'
            }}" />
    </function>
    """
        base_xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<odoo>{new_function}
</odoo>
"""
        if target_path.exists():
            content = target_path.read_text(encoding='utf-8')
            if "</odoo>" in content:
                updated_content = content.replace("</odoo>", f"{new_function}\n</odoo>")
            else:
                updated_content = content + "\n" + new_function + "\n</odoo>"
        else:
            updated_content = base_xml

        # Write back to file
        try:
            target_path.write_text(updated_content, encoding='utf-8')
        except Exception as e:
            raise Exception(f"Unable to write website_theme_apply.xml file: {e}")

    return

def order_ir_attachment_post(destination_module_path):
    # Order ir attachment record only if after ir_attachment_ contains number
    path_ir_attachment_post = Path(destination_module_path + '/demo/' + 'ir_attachment_post.xml')
    if path_ir_attachment_post.exists():
        root_ir_attachment_post = get_etree_content(path_ir_attachment_post)
        all_records = root_ir_attachment_post.xpath("//record")
        records = list(filter(lambda x: re.fullmatch(r'ir_attachment_\d+', x.get('id', '')), all_records))
        sorted_records = sorted(records, key = lambda x: int(x.get('id').split("_")[-1]))

        for record in records:
            root_ir_attachment_post.remove(record)
        for record in reversed(sorted_records):
            root_ir_attachment_post.insert(0, record)

        write_etree_content(path_ir_attachment_post, root_ir_attachment_post)
    
    return

def remove_unused_ir_attachment_post(destination_base_path, destination_module_path):
    path_ir_attachment_post = Path(destination_module_path + '/demo/' + 'ir_attachment_post.xml')
    path_ir_ui_view = Path(destination_module_path + '/demo/' + 'ir_ui_view.xml')
    if path_ir_attachment_post.exists() and path_ir_ui_view.exists():
        root_ir_attachment_post = get_etree_content(path_ir_attachment_post)
        content_ir_ui_view = path_ir_ui_view.read_text(encoding="utf-8")
        records = root_ir_attachment_post.xpath("//record")
        unused_ir_attachment_post_ids = []
        unused_files = []
        for record in records:
            key_field = record.xpath(".//field[@name='key']")
            name_field = record.xpath(".//field[@name='name']")
            if key_field or name_field:
                # check key text in ir_ui_view.xml file if not found store in list
                if key_field:
                    key = key_field[0].text
                    file_name = record.xpath(".//field[@name='datas']")[0].get('file')
                    if key not in content_ir_ui_view:
                        unused_ir_attachment_post_ids.append(record)
                        if file_name:
                            unused_files.append(file_name)
                # check name text in ir_ui_view.xml file if not found store in list
                elif name_field:
                    name = name_field[0].text
                    file_name = record.xpath(".//field[@name='datas']")[0].get('file')
                    if name not in content_ir_ui_view:
                        unused_ir_attachment_post_ids.append(record)
                        if file_name:
                            unused_files.append(file_name)
            else:
                unused_ir_attachment_post_ids.append(record)
        # Remove record and delete file if not need in ir_ui_view.xml file
        for unused_ir_attachment_post_id in unused_ir_attachment_post_ids:
            root_ir_attachment_post.remove(unused_ir_attachment_post_id)
        for unused_file in unused_files:
            file_path = Path(destination_base_path + unused_file)
            if file_path.exists():
                os.remove(file_path)

        write_etree_content(path_ir_attachment_post, root_ir_attachment_post)

    return

def clean_knowledge_article(destination_module_path):
    # Delete all record of knowledge article and kept only record which id ends with welcome_article
    path_knowledge_article = Path(destination_module_path + '/data/' + 'knowledge_article.xml')
    if path_knowledge_article.exists():
        root_knowledge_article = get_etree_content(path_knowledge_article)
        records = root_knowledge_article.xpath("//record")
        for record in records:
            for field in record.xpath('.//field[@name="last_edition_uid"]'):
                record.remove(field)
            if not record.xpath('//field[@name="is_locked"]'):
                new_field = etree.Element("field", name="is_locked")
                new_field.text = "1"
                record.append(new_field)
            record_id = record.get('id', '')
            if record_id.endswith("welcome_article"):
                record.set("id", "welcome_article")  # Rename the ID
                for field in record:
                    if field.text and '<div' in field.text:
                        field.text = etree.CDATA(field.text)
            else:
                root_knowledge_article.remove(record)

        write_etree_content(path_knowledge_article, root_knowledge_article)
    return

def remove_ondelete_false_field(destination_module_path):
    # From ir_model_fields.xml remove field on_delete if type id not many2one or one2many
    path_ir_model_fields = Path(destination_module_path + '/data/' + 'ir_model_fields.xml')
    if path_ir_model_fields.exists():
        root_ir_model_field = get_etree_content(path_ir_model_fields)
        records = root_ir_model_field.xpath("//record")
        for record in records:
            field_type_elem = record.xpath(".//field[@name='ttype']")
            if not field_type_elem:
                continue
            field_type = field_type_elem[0].text.strip()
            if field_type not in ['many2one', 'one2many']:
                for field in record.xpath(".//field[@name='on_delete']"):
                    if field.get('eval') == 'False':
                        record.remove(field)
            for field in record.xpath(".//field[@name='compute']"):
                original_text = field.text
                if original_text:
                    field.text = etree.CDATA(original_text)

        write_etree_content(path_ir_model_fields, root_ir_model_field)

    return
    
def add_demo_payment_provider(destination_module_path, manifest_demo_file_list, port, db_name):
    file_name = 'payment_provider_demo.xml'
    if check_website_sale_installed(port, db_name):
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
<odoo noupdate="1">
    <function name="button_immediate_install" model="ir.module.module" eval="[ref('base.module_payment_demo')]"/>
</odoo>
        """
        manifest_demo_file_dict = {}
        manifest_demo_file_dict['file_name'] = file_name
        manifest_demo_file_dict['ref_name'] = []
        manifest_demo_file_list.append(manifest_demo_file_dict)

        Path(destination_module_path + '/demo/' + file_name).write_text(xml_content, encoding='utf-8')
    return

def check_website_sale_installed(port, db_name):
        # Prepare the JSON-RPC payload to search for the 'website_sale' module
        
        session, uid = session_authentication(db_name, port)
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name, uid, PASSWORD,
                    "ir.module.module", "search_read",
                    [[["name", "=", "website_sale"]]],
                    {"fields": ["state"], "limit": 1}
                ]
            },
            "id": 2
        }

        # Send the request to the server and parse the JSON response
        response = session.post(f"{BASE_URL}{port}/jsonrpc", json=payload).json()
        
        # Return the list of matched module(s) with their state
        if response["result"]:
            return response["result"][0]['state'] == 'installed'

def clean_module(ind_name, ind_category, db_name, module_path, port, destination_base_path):
    Ind_name = re.sub(r'[_-]', ' ', ind_name)
    Ind_name = Ind_name.title()
    Ind_category = re.sub(r'[_-]', ' ', ind_category)
    Ind_category = Ind_category.title()
    automated['category'] = Ind_category

    destination_module_path = destination_base_path + '/' + ind_name
    directory = module_path

    fields_info_list = get_fields_info(db_name, port)

    scss_content_list = []
    manifest_demo_file_list = []
    for root, dirs, files in os.walk(directory):
        current_dir = root.split(directory)[1] + '/'
        for d in dirs:
            os.makedirs(destination_module_path + current_dir + d, exist_ok=True)
        for file_name in files:
            ext = file_name.rsplit('.')[1] if '.' in file_name else ''
            if ext == 'xml':
                content = Path(root + '/' + file_name).read_text(encoding="utf-8")

                content = edit_xml_content(ind_name, content)
                unwanted_fields = ['color', 'sequence', 'inherited_permission', 'access_token', 'document_token', 'peppol_verification_state', 'uuid']
                # Removing unwanted fields
                content = remove_unwanted_fields(content, unwanted_fields)

                xml_root = etree.fromstring(content.encode("utf-8"))
                # Get all ref from all records
                ref_name_list = list(set([
                    field.get('ref')
                    for record in xml_root.xpath("//record")
                    for field in record
                    if field.get('ref') and '.' not in field.get('ref')
                ]))
                # if demo files dont have record simply append
                if current_dir.endswith('/demo/') and not xml_root.xpath("//record"):
                    manifest_demo_file_dict = {}
                    manifest_demo_file_dict['file_name'] = file_name
                    manifest_demo_file_dict['ref_name'] = ref_name_list
                    manifest_demo_file_list.append(manifest_demo_file_dict)

                for record in xml_root.xpath("//record"):

                    unorder_manifest_demo_files(manifest_demo_file_list, current_dir, file_name, ref_name_list, record)
                    # Removing field according to models
                    model_name = record.get('model')
                    if not model_name:
                        continue
                    
                    content = remove_model_based_fields(model_name, content)

                    # Removing computed fields which is not inverse
                    content = remove_computed_fields(fields_info_list, model_name, record, content)
                
                if file_name == 'ir_default.xml':
                    content = re.sub(r"<odoo>", '<odoo noupdate="1">', content)

                if file_name == "knowledge_article.xml":
                    content = re.sub('<odoo noupdate="1">', '<odoo>', content)
                    Path(destination_module_path + current_dir + file_name).write_text(content, encoding='utf-8')
                    continue

                Path(destination_module_path + current_dir + file_name).write_text(content, encoding='utf-8')

            elif ext in ['py', 'txt']:
                if file_name != '__manifest__.py':
                    continue
                manifest = literal_eval(Path(root + '/' + file_name).read_text(encoding="utf-8"))
                with open(destination_module_path + '/__manifest__.py', 'w', encoding="utf-8") as f:
                    f.write('{\n')
                    for k, v in manifest.items():
                        if k == 'name':
                            f.write(f"    '{k}': '{Ind_name}',\n")
                        elif k == 'description':
                            continue
                        elif k not in automated:
                            if isinstance(v, list):
                                f.write(f"    '{k}': [\n")
                                for item in v:
                                    unwanted_depends = [
                                        'base_module',
                                        '__import__',
                                        'account_invoice_extract',
                                        'account_online_synchronization',
                                        'account_peppol',
                                        'auth_totp_mail',
                                        'base_install_request',
                                        'crm_iap_enrich',
                                        'crm_iap_mine',
                                        'partner_autocomplete',
                                        'pos_epson_printer',
                                        'sale_async_emails',
                                        'snailmail_account',
                                        'web_grid',
                                        'web_studio',
                                        'social_push_notifications',
                                        'appointment_sms',
                                        'website_knowledge',
                                        'base_vat',
                                        'product_barcodelookup',
                                        'snailmail_account_followup',
                                        'base_geolocalize',
                                        'gamification',
                                        'l10n_be_pos_sale',
                                        'pos_sms',
                                        'pos_settle_due',
                                        'website_partner',
                                        'website_project',
                                        'project_sms',
                                        ]
                                    if k == 'depends' and (item in unwanted_depends or item.startswith('theme_')):
                                        continue
                                    f.write(f"        '{item}',\n")
                                if k == 'data':
                                    f.write("        'data/mail_message.xml',\n")
                                    f.write("        'data/knowledge_article_favorite.xml',\n")
                                    f.write("        'data/knowledge_tour.xml',\n")
                                f.write("    ],\n")
                            else:
                                f.write(f"    '{k}': '{v}',\n")
                        else:
                            f.write(f"    '{k}': '{automated[k]}',\n")
                    f.write('}\n')

            elif not ext:
                shutil.copy(root + '/' + file_name, destination_module_path + current_dir + file_name)

            elif current_dir.endswith('/ir_attachment/') and ext != "scss":
                shutil.copy(root + '/' + file_name, destination_module_path + current_dir + file_name)

            elif current_dir.endswith('/ir_attachment/') and ext == "scss":
                scss_content_dict = {}

                scss_content = Path(root + '/' + file_name).read_text(encoding="utf-8")
                # Define a regex pattern to match the content inside the o-map-omit in SCSS file
                scss_pattern = re.compile(r'o-map-omit\(\(\s*(.*?)\s*\)\)', re.DOTALL)
                scss_match = scss_pattern.search(scss_content)

                if scss_match:
                    inner_scss_content = scss_match.group(1)  # Extract inner contents
                    scss_content_dict['inner_scss_content'] = inner_scss_content
                    if 'color' in file_name:
                        scss_content_dict['url'] = "/website/static/src/scss/options/colors/" + file_name
                    else:
                        scss_content_dict['url'] = "/website/static/src/scss/options/" + file_name

                    scss_content_list.append(scss_content_dict)
                else:
                    continue

    # making function of custom scss data on website_theme_apply.xml
    write_scss_function(destination_module_path, scss_content_list)

    remove_ondelete_false_field(destination_module_path)

    # Writing record in ascending order according to id and remove unused records
    remove_unused_ir_attachment_post(destination_base_path, destination_module_path)
    order_ir_attachment_post(destination_module_path)

    # Keeping only welcome article
    clean_knowledge_article(destination_module_path)

    # Add payment_provider_demo.xml file in demo folder if website_sale is installed
    add_demo_payment_provider(destination_module_path, manifest_demo_file_list, port, db_name)

    # Overiting demo file order in manifest
    arrange_demo_files(destination_module_path, ind_name,  manifest_demo_file_list)

    for file, content in mandatory_files.items():
        directory, _ = os.path.split(file)
        os.makedirs(destination_module_path + directory, exist_ok=True)
        Path(destination_module_path + file).write_text(content.format(ind_name=ind_name, Ind_name=Ind_name), encoding='UTF-8')



# ====================================================
#              Main Function         
# ====================================================

def main():
    parser = argparse.ArgumentParser(description="Industry Automation Script")

    parser.add_argument('--module_name', required=True, help="Name of the module")
    parser.add_argument('--db_version', required=True, help="Database version")
    parser.add_argument('--category', required=True, help="Module category")
    parser.add_argument('--dump_path', required=True, help="Path to the dump zip file")
    parser.add_argument('--destination_path', default="/home/odoo/Pictures/custom_modules", help="Path to save the cleaned module")
    parser.add_argument('--master_password', required=True, help="Odoo master password")

    args = parser.parse_args()

    task = ProcessDb(
        module_name=args.module_name,
        db_version=args.db_version,
        category=args.category,
        dump_path=args.dump_path,
        destination_path=args.destination_path,
        master_password=args.master_password,
    )

    task.process_dump_task()

if __name__ == "__main__":
    main()