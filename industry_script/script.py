#!/usr/bin/env python3
# To run
# odoo folder => PYTHONPATH=./community python3 tutorials/industry_script/script.py -d <database_name> -m <module_name> -c <category_name> -p <module_path>

import sys
from pathlib import Path
import re
import os
from ast import literal_eval
import shutil
from lxml import etree

import odoo
import odoo.tools.config
from odoo import api, SUPERUSER_ID

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

def check_command(sys_argv):
    if '-m' not in sys_argv or '-c' not in sys_argv or '-d' not in sys_argv or '-p' not in sys_argv:
        exit("Missing required parameter: \n\nUsage: script.py -d <database_name> -m <module_name> -c <category_name> -p <module_path>")

    database_name_index = sys_argv.index('-d') + 1
    module_name_index = sys_argv.index('-m') + 1
    category_name_index = sys_argv.index('-c') + 1
    module_path_index = sys_argv.index('-p') + 1

    ind_name = sys_argv[module_name_index]
    ind_category = sys_argv[category_name_index]
    db_name = sys_argv[database_name_index]
    module_path = sys_argv[module_path_index]

    if os.path.isdir(ind_name) and not ((len(sys_argv) > 9) and (sys_argv[9] == 'force')):
        exit("Industry already exists. Change name or delete the previous attempt, or add 'force' at the end overwrite.")

    return (ind_name, ind_category, db_name, module_path)

def setup_odoo_env(db_name):
    try:
        DB_NAME = db_name
        # Set config manually
        odoo.tools.config['db_name'] = DB_NAME
        odoo.tools.config['addons_path'] = '/home/odoo/odoo/community/addons,/home/odoo/odoo/enterprise'
        odoo.tools.config['log_level'] = 'error'

        # # Setup environment
        # registry = odoo.modules.registry.Registry.new(DB_NAME)  # Create the registry for the tattoo_db
        # registry.setup_signaling()  # ensures that the registry is fully initialized and ready to use

        # Initialize cursor and environment
        cr = odoo.sql_db.db_connect(DB_NAME).cursor()  # execute SQL queries directly on the tattoo_db database, cursor is the interface for executing SQL queries
        env = api.Environment(cr, SUPERUSER_ID, {})  # gives access to models and allows you to interact with the database using Python objects

        return cr, env
    except Exception as e:
        exit(f"Error while setting up Odoo environment for database '{db_name}': {e}")

def get_etree_content(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        etree_content = etree.fromstring(content.encode("utf-8"))
        return etree_content
    except Exception as e:
        raise Exception(f"Error while getting etree content of file ({file_path}): {e}")

def write_etree_content(file_path, etree_content):
    try:
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

    context_studio = re.compile(" context=\"{'studio': True}\"")
    content = context_studio.sub('', content)
    studio_mod = re.compile("studio_customization\.")
    content = studio_mod.sub('', content)
    studio_link = re.compile("studio_customization/")
    content = studio_link.sub(ind_name + '/', content)

    pattern_base_module_forcecreate = re.compile(r'(<record\s+[^>]*id="base_module\.[^"]*"[^>]*?")\s+forcecreate="1"')
    content = pattern_base_module_forcecreate.sub(r"\1", content)

    pattern_base_module = re.compile("base_module\.")
    content = pattern_base_module.sub("", content)

    pattern_import = re.compile("__import__\.")
    content = pattern_import.sub("", content)

    pattern_res_users_7_res_partner = re.compile("res_users_\w+")
    content = pattern_res_users_7_res_partner.sub("base.user_admin", content)

    pattern_ir_ui_view = re.compile(r"obj\(\)\.env\.ref\(\'ir_ui_view_")
    content = pattern_ir_ui_view.sub(f"obj().env.ref('{ind_name}.ir_ui_view_", content)

    pattern_ir_ui_view_key = re.compile(r'(<field name="key">)website.homepage(</field>)')
    content = pattern_ir_ui_view_key.sub(rf'\1{ind_name}.homepage\2', content)

    pattern_href_url = re.compile(r'https://(?!www\.)([^/]+)\.odoo\.com')
    content = pattern_href_url.sub(f'https://{ind_name.replace("_", "-")}.odoo.com', content)

    pattern_url = re.compile(r'(<field name="url">)https://[^/]+(.*?</field>)')
    content = pattern_url.sub(r'\1\2', content)

    pattern_product_uom_unit = re.compile(r'\s*<field[^>]*ref="uom.[^"]*"[^>]*\s*/>')
    content = pattern_product_uom_unit.sub('', content)

    pattern_product_uom_false = re.compile(r'\s*<field name="product_uom_qty" eval="False"[^>]*\s*/>')
    content = pattern_product_uom_false.sub('', content)
    
    pattern_knowledge_article_keyword = re.compile(r'(/documentation/)[^/]+')
    content = pattern_knowledge_article_keyword.sub(r'\1latest', content)

    return content

def remove_computed_fields(env, model_name, record, content):
    model = env.get(model_name)
    if model is None:
        return content

    fields_set_in_record = {
        field.get('name') for field in record.xpath('.//field')
    }

    for field_name in fields_set_in_record:
        field_obj = model._fields.get(field_name)

        if field_obj and (field_obj.compute and field_obj.readonly):

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
    for unwanted_field in unwanted_fields:
        pattern_regular = rf'\s*<field name="{unwanted_field}">.*?</field>'
        pattern_self_closing = rf'\s*<field name="{unwanted_field}"[^>]*\s*/>'

        content = re.sub(pattern_regular, "", content, flags=re.DOTALL)
        content = re.sub(pattern_self_closing, "", content)

    return content

def remove_model_based_fields(model_name, content):

    model_field_map = {
        'calendar.event': ['start', 'stop'],
        'crm.lead': ['email_from', 'company_id', 'country_id', 'city', 'street', 'partner_name', 'contact_name', 'zip', 'reveal_id', 'medium_id', 'date_closed', 'email_state', 'date_open', 'email_domain_criterion', 'won_status', 'street2', 'phone', 'state_id'],
        'event.event': ['kanban_state_label'],
        'hr.department': ['complete_name', 'master_department_id'],
        'pos.config': ['last_data_change'],
        'pos.order': ['date_order', 'state', 'last_order_preparation_change', 'pos_reference', 'ticket_code', 'email', 'company_id'],
        'pos.order.line': ['full_product_name', 'qty_delivered', 'price_unit', 'total_cost'],
        'pos.payment.method': ['is_cash_count'],
        'pos.session': ['name', 'start_at', 'stop_at', 'state'],
        'product.pricelist.item': ['date_start', 'date_end'],
        'product.template': ['base_unit_count'],
        'purchase.order': ['date_order', 'date_approve', 'state', 'date_planned'],
        'purchase.order.line': ['date_planned', 'name'],
        'res.partner': ['supplier_rank', 'partner_gid'],
        'sale.order': ['date_order', 'prepayment_percent', 'delivery_status', 'amount_unpaid', 'warehouse_id', 'origin'],
        'sale.order.line': ['technical_price_unit', 'warehouse_id'],
        'sale.order.template': ['prepayment_percent'],
        'sign.item': ['transaction_id'],
    }

    # Retrieve the list of unwanted fields for the given model
    unwanted_fields = model_field_map.get(model_name, [])

    # Remove those fields using the previously defined helper
    content = remove_unwanted_fields(content, unwanted_fields)

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

def add_require_depends(depends_list):
    new_depends = ['knowledge']
    depends_list = sorted(set(depends_list + new_depends))
    return depends_list

def arrange_demo_files(ind_name, manifest_demo_file_list):
    try:
        old_file = Path(ind_name + "/demo/ir_ui_view.xml")
        new_file = Path(ind_name + "/demo/website_view.xml")
        os.rename(old_file, new_file)
    except Exception as e:
        raise Exception(f"Error while renaming file: {e}")

    new_manifest_demo_file_list = []
    for file_list in manifest_demo_file_list:
        if file_list['file_name'] == "ir_ui_view.xml":
            file_list['file_name'] = "website_view.xml"
        if file_list['file_name'] not in new_manifest_demo_file_list:
            new_manifest_demo_file_list.append(file_list['file_name'])

    unique_manifest_demo_file_list = [ 'demo/' + file_name for file_name in new_manifest_demo_file_list ]

    try:
        manifest_path = Path(ind_name + '/__manifest__.py')
        manifest = literal_eval(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise Exception(f"Unable to read manifest file: {e}")
    manifest['depends'] = add_require_depends(manifest['depends'])
    # Check files from list if no record then dlete file and remove from manifest
    check_files = ['ir_attachment_pre.xml', 'knowledge_cover.xml', 'mail_template.xml', 'product_pricelist.xml']
    for check_file in check_files:
        file_path = Path(ind_name + '/data/' + check_file)
        if file_path.exists():
            etree_content = get_etree_content(file_path)
            records = etree_content.xpath("//record")
            if len(records) == 0:
                os.remove(file_path)
                manifest['data'].remove('data/' + check_file)

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

def get_scss_content(scss_content_list, root, file_name):
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
    
    return

def write_scss_function(ind_name, scss_content_list):
    if scss_content_list:
        target_path = Path(ind_name + '/demo/' + 'website_theme_apply.xml')
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

def order_ir_attachment_post(ind_name):
    path_ir_attachment_post = Path(ind_name + '/demo/' + 'ir_attachment_post.xml')
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

def remove_unused_ir_attachment_post(ind_name):
    path_ir_attachment_post = Path(ind_name + '/demo/' + 'ir_attachment_post.xml')
    path_ir_ui_view = Path(ind_name + '/demo/' + 'ir_ui_view.xml')
    if path_ir_attachment_post.exists() and path_ir_ui_view.exists():
        root_ir_attachment_post = get_etree_content(path_ir_attachment_post)
        content_ir_ui_view = path_ir_ui_view.read_text(encoding="utf-8")
        records = root_ir_attachment_post.xpath("//record")
        unused_ir_attachment_post_ids = []
        unused_files = []
        for record in records:
            key_field = record.xpath(".//field[@name='key']")
            name_field = record.xpath(".//field[@name='name']")
            datas_field = record.xpath(".//field[@name='datas']")
            if key_field or name_field:
                # check key or name in ir_ui_view.xml file if not found store in list
                key = key_field[0].text if key_field else None
                name = name_field[0].text if name_field else None
                file_name = record.xpath(".//field[@name='datas']")[0].get('file') if datas_field else None
                # file_name = record.xpath(".//field[@name='datas']")[0].get('file')
                if not ((key and key in content_ir_ui_view) or (name and name in content_ir_ui_view)):
                    unused_ir_attachment_post_ids.append(record)
                    if file_name:
                        unused_files.append(file_name)
            else:
                unused_ir_attachment_post_ids.append(record)

        for unused_ir_attachment_post_id in unused_ir_attachment_post_ids:
            root_ir_attachment_post.remove(unused_ir_attachment_post_id)
        for unused_file in unused_files:
            file_path = Path(unused_file)
            if file_path.exists():
                os.remove(file_path)

        write_etree_content(path_ir_attachment_post, root_ir_attachment_post)

    return

def clean_knowledge_article(ind_name):
    # Remove record of knowledge article except record which have welcome_article in id
    path_knowledge_article = Path(ind_name + '/data/' + 'knowledge_article.xml')
    if path_knowledge_article.exists():
        root_knowledge_article = get_etree_content(path_knowledge_article)
        records = root_knowledge_article.xpath("//record")
        for record in records:
            for field in record.xpath('.//field[@name="last_edition_uid"]'):
                record.remove(field)
            if not record.xpath('.//field[@name="is_locked"]'):
                new_field = etree.Element("field", name="is_locked", eval="True")
                record.append(new_field)
            record_id = record.get('id', '')
            if '.' not in record_id:
                record.set("id", "welcome_article")  # Rename the ID
                for field in record:
                    if field.text and '<div' in field.text:
                        field.text = etree.CDATA(field.text)
            else:
                root_knowledge_article.remove(record)

        write_etree_content(path_knowledge_article, root_knowledge_article)
    return

def remove_ondelete_false_field(ind_name):
    path_ir_model_fields = Path(ind_name + '/data/' + 'ir_model_fields.xml')
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

def check_website_sale_install(env, ind_name, manifest_demo_file_list):
    file_name = 'payment_provider_demo.xml'
    ir_module_module = env.get('ir.module.module')
    if ir_module_module._get('website_sale').state == 'installed':
        xml_content = """<?xml version='1.0' encoding='UTF-8'?>
<odoo noupdate="1">
    <function name="button_immediate_install" model="ir.module.module" eval="[ref('base.module_payment_demo')]"/>
</odoo>
        """
        manifest_demo_file_dict = {}
        manifest_demo_file_dict['file_name'] = file_name
        manifest_demo_file_dict['ref_name'] = []
        manifest_demo_file_list.append(manifest_demo_file_dict)

        Path(ind_name + '/demo/' + file_name).write_text(xml_content, encoding='utf-8')
    return

def remove_record_not_created_by_user(ind_name, file_name):
    # Remove records if record is not user created
    path_file = Path(ind_name + '/data/' + file_name)
    if path_file.exists():
        root_file = get_etree_content(path_file)
        records = root_file.xpath("//record")
        for record in records:
            record_id = record.get('id')
            if '.' in record_id:
                root_file.remove(record)
        write_etree_content(path_file, root_file)
    return

def remove_default_pricelist(ind_name):
    # Remove record which name id default
    path_product_pricelist = Path(ind_name + '/data/' + 'product_pricelist.xml')
    if path_product_pricelist.exists():
        root_product_pricelist = get_etree_content(path_product_pricelist)
        records = root_product_pricelist.xpath("//record")
        for record in records:
            name_key = record.xpath(".//field[@name='name']")
            if name_key and (name_key[0].text == 'Default' or name_key[0].text == 'default'):
                root_product_pricelist.remove(record)
        
        write_etree_content(path_product_pricelist, root_product_pricelist)

    return

def add_theme_immediate_install_function(ind_name):
    website_path = Path(ind_name + '/demo/' + 'website.xml')
    if website_path.exists():
        etree_content = get_etree_content(website_path)
        theme_id = etree_content.xpath("//field[@name='theme_id']")[0].get('ref')
        if theme_id:
            new_function = f"""<function name="button_immediate_install" model="ir.module.module" eval="[ref('{theme_id}', raise_if_not_found=False)]"/>"""
            base_xml = f"""<?xml version='1.0' encoding='UTF-8'?>
<odoo>{new_function}
</odoo>
"""
            target_path = Path(ind_name + '/demo/' + 'website_theme_apply.xml')
            if target_path.exists():
                content = target_path.read_text(encoding='utf-8')
                updated_content = content.replace("<odoo>", f"<odoo>\n\t{new_function}\n")
            else:
                updated_content = base_xml

            # Write back to file
            try:
                target_path.write_text(updated_content, encoding='utf-8')
            except Exception as e:
                raise Exception(f"Unable to write website_theme_apply.xml file: {e}")
    return

def clean_sale_order_line_record(ind_name):
    target_path = Path(ind_name + '/demo/' + 'sale_order_line.xml')
    if target_path.exists():
        etree_content = get_etree_content(target_path)
        records = etree_content.xpath("//record")
        for record in records:
            display_type_elem = record.xpath(".//field[@name='display_type']")
            if display_type_elem and display_type_elem[0].text and display_type_elem[0].text.strip() == 'line_section':
                for field in record.xpath(".//field[@name='name']"):
                    original_text = field.text
                    if original_text:
                        field.text = etree.CDATA(original_text)
            else:
                for field in record.xpath(".//field[@name='name']"):
                    record.remove(field)

        write_etree_content(target_path, etree_content)

    return

def main():
    cr = None
    try:
        ind_name, ind_category, db_name, module_path = check_command(sys.argv)
        cr, env = setup_odoo_env(db_name)

        Ind_name = re.sub(r'[_-]', ' ', ind_name)
        Ind_name = Ind_name.title()
        Ind_category = re.sub(r'[_-]', ' ', ind_category)
        Ind_category = Ind_category.title()
        automated['category'] = Ind_category

        directory = "/home/odoo/odoo/tutorials/industry_script/studio_customization"
        # directory = module_path

        scss_content_list = []
        manifest_demo_file_list = []
        for root, dirs, files in os.walk(directory):
            current_dir = root.split(directory)[1] + '/'
            for d in dirs:
                os.makedirs(ind_name + current_dir + d, exist_ok=True)
            for file_name in files:
                ext = file_name.rsplit('.')[1] if '.' in file_name else ''
                if ext == 'xml':
                    content = Path(root + '/' + file_name).read_text(encoding="utf-8")

                    content = edit_xml_content(ind_name, content)
                    unwanted_fields = ['color', 'sequence', 'inherited_permission', 'access_token', 'document_token', 'peppol_verification_state', 'uuid', 'analytic_distribution']
                    
                    # Removing unwanted fields
                    content = remove_unwanted_fields(content, unwanted_fields)

                    if file_name == 'ir_default.xml':
                        content = re.sub(r"<odoo>", '<odoo noupdate="1">', content)

                    xml_root = etree.fromstring(content.encode("utf-8"))

                    ref_name_list = list(set([
                        field.get('ref')
                        for record in xml_root.xpath("//record")
                        for field in record
                        if field.get('ref') and '.' not in field.get('ref')
                    ]))

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
                        content = remove_computed_fields(env, model_name, record, content)

                    if file_name == "knowledge_article.xml":
                        content = re.sub('<odoo noupdate="1">', '<odoo>', content)
                        Path(ind_name + current_dir + file_name).write_text(content, encoding='utf-8')
                        continue

                    Path(ind_name + current_dir + file_name).write_text(content, encoding='utf-8')

                elif ext in ['py', 'txt']:
                    if file_name != '__manifest__.py':
                        continue
                    manifest = literal_eval(Path(root + '/' + file_name).read_text(encoding="utf-8"))
                    with open(ind_name + '/__manifest__.py', 'w', encoding="utf-8") as f:
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
                                            '__import__',
                                            'account_auto_transfer',
                                            'account_invoice_extract',
                                            'account_online_synchronization',
                                            'account_peppol',
                                            'appointment_sms',
                                            'auth_totp_mail',
                                            'base_geolocalize',
                                            'base_install_request',
                                            'base_module',
                                            'base_vat',
                                            'crm_iap_enrich',
                                            'crm_iap_mine',
                                            'currency_rate_live',
                                            'gamification',
                                            'l10n_be_pos_sale',
                                            'partner_autocomplete',
                                            'pos_epson_printer',
                                            'pos_settle_due',
                                            'pos_sms',
                                            'privacy_lookup',
                                            'product_barcodelookup',
                                            'project_sms',
                                            'project_todo',
                                            'sale_async_emails',
                                            'snailmail_account',
                                            'snailmail_account_followup',
                                            'social_push_notifications',
                                            'web_grid',
                                            'web_studio',
                                            'website_knowledge',
                                            'website_partner',
                                            'website_project',
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
                    shutil.copy(root + '/' + file_name, ind_name + current_dir + file_name)

                elif current_dir.endswith('/ir_attachment/') and ext != "scss":
                    shutil.copy(root + '/' + file_name, ind_name + current_dir + file_name)

                elif current_dir.endswith('/ir_attachment/') and ext == "scss":
                    get_scss_content(scss_content_list, root, file_name)

        # making function of custom scss data on website_theme_apply.xml
        write_scss_function(ind_name, scss_content_list)

        # Remove fields explicitly marked with ondelete=False
        remove_ondelete_false_field(ind_name)

        # Remove record from files which are not user created
        remove_file_names = ['ir_attachment_pre.xml', 'knowledge_cover.xml', 'mail_template.xml']
        for remove_file_name in remove_file_names:
            remove_record_not_created_by_user(ind_name, remove_file_name)
        
        # Remove default pricelist from product_pricelist.xml
        remove_default_pricelist(ind_name)

        # Writing record in ascending order according to id and remove unused records
        remove_unused_ir_attachment_post(ind_name)
        order_ir_attachment_post(ind_name)

        # Keeping only welcome article
        clean_knowledge_article(ind_name)

        # Add payment_provider_demo.xml file in demo folder if website_sale is installed
        check_website_sale_install(env, ind_name, manifest_demo_file_list)
        
        # Add immediate install function for the theme module in demo XML files
        add_theme_immediate_install_function(ind_name)

        # Remove name field if display_type is not line_section
        clean_sale_order_line_record(ind_name)

        # Arrange and Overiting content of manifest
        arrange_demo_files(ind_name, manifest_demo_file_list)

        for file, content in mandatory_files.items():
            directory, _ = os.path.split(file)
            os.makedirs(ind_name + directory, exist_ok=True)
            Path(ind_name + file).write_text(content.format(ind_name=ind_name, Ind_name=Ind_name), encoding='UTF-8')

    finally:
        if cr:
            cr.close()

if __name__ == "__main__":
    main()
