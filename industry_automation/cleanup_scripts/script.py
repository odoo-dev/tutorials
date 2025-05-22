#!/usr/bin/env python3

import sys
from pathlib import Path
import re
import os
from ast import literal_eval
import shutil
from lxml import etree
import requests

BASE_URL = "http://localhost:"
PASSWORD = "admin"
LOGIN = "admin"

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

def get_fields_info(db_name, port):

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

    payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    db_name,
                    result["uid"],
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

def check_command(sys_argv):
    # check cli for valid arguments
    if '-m' not in sys_argv or '-c' not in sys_argv or '-d' not in sys_argv or '-p' not in sys_argv or '--port' not in sys_argv:
        exit("Missing required parameter: \n\nUsage: script.py -d <database_name> -m <module_name> -c <category_name> -p <module_path> --port <port>")

    # Get index of db_name, module name, category name, path, port
    database_name_index = sys_argv.index('-d') + 1
    module_name_index = sys_argv.index('-m') + 1
    category_name_index = sys_argv.index('-c') + 1
    module_path_index = sys_argv.index('-p') + 1
    port_index = sys_argv.index('--port') + 1

    ind_name = sys_argv[module_name_index]
    ind_category = sys_argv[category_name_index]
    db_name = sys_argv[database_name_index]
    module_path = sys_argv[module_path_index]
    port = sys_argv[port_index]

    # Industry already exist and cli dont have force then exit with warning
    if os.path.isdir(ind_name) and not ((len(sys_argv) > 11) and (sys_argv[11] == 'force')):
        exit("Industry already exists. Change name or delete the previous attempt, or add 'force' at the end overwrite.")

    return (ind_name, ind_category, db_name, module_path, port)

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
    
def main(ind_name, ind_category, db_name, module_path, port, destination_base_path):
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

    # Overiting demo file order in manifest
    arrange_demo_files(destination_module_path, ind_name,  manifest_demo_file_list)

    for file, content in mandatory_files.items():
        directory, _ = os.path.split(file)
        os.makedirs(destination_module_path + directory, exist_ok=True)
        Path(destination_module_path + file).write_text(content.format(ind_name=ind_name, Ind_name=Ind_name), encoding='UTF-8')
