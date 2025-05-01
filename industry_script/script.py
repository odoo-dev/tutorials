#!/usr/bin/env python3
# To run
# odoo folder => PYTHONPATH=./community python3 tutorials/industry_script/script.py -m <module_name> -c <category_name>

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

DB_NAME = "tattoo"
# Set config manually
odoo.tools.config['db_name'] = DB_NAME
odoo.tools.config['addons_path'] = './community/addons,./enterprise'
odoo.tools.config['log_level'] = 'error'

# Setup environment
registry = odoo.modules.registry.Registry.new(DB_NAME)  # Create the registry for the tattoo_db
registry.setup_signaling()  # ensures that the registry is fully initialized and ready to use

# Initialize cursor and environment
cr = odoo.sql_db.db_connect(DB_NAME).cursor()  # execute SQL queries directly on the tattoo_db database, cursor is the interface for executing SQL queries
env = api.Environment(cr, SUPERUSER_ID, {})  # gives access to models and allows you to interact with the database using Python objects




automated = {
    'author': 'Odoo S.A.',
    'category': 'TODO',
    'description': '',
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
            position: "bottom",
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
    "/data/knowledge_tour.xml": """<?xml version="1.0" encoding="utf-8"?>
<odoo noupdate="1">
    <record id="knowledge_tour" model="web_tour.tour">
        <field name="name">{ind_name}_knowledge_tour</field>
        <field name="sequence">2</field>
        <field name="rainbow_man_message">Welcome! Happy exploring.</field>
    </record>
</odoo>
""",
}


def main():
    if '-m' not in sys.argv:
        exit("Missing required parameter: -m <module_name>\n\nUsage: script.py -m <module_name> -c <category_name>")
    if '-c' not in sys.argv:
        exit("Missing required parameter: -c <module_name>\n\nUsage: script.py -m <module_name> -c <category_name>")

    model_name_index = sys.argv.index('-m') + 1
    category_name_index = sys.argv.index('-c') + 1

    ind_name = sys.argv[model_name_index]
    Ind_name = ind_name.capitalize()

    ind_category = sys.argv[category_name_index]
    Ind_category = re.sub(r'[_-]', ' ', ind_category)
    Ind_category = Ind_category.title()

    automated['category'] = Ind_category

    if os.path.isdir(ind_name) and not ((len(sys.argv) > 5) and (sys.argv[5] == 'force')):
        exit("industry already exists, change name or delete previous try")
    directory = "/home/odoo/odoo/tutorials/industry_script/studio_customization"
    scss_content_list = []
    for root, dirs, files in os.walk(directory):
        current_dir = root.split(directory)[1] + '/'
        for d in dirs:
            os.makedirs(ind_name + current_dir + d, exist_ok=True)
        for file_name in files:
            ext = file_name.rsplit('.')[1] if '.' in file_name else ''
            if ext == 'xml':
                content = Path(root + '/' + file_name).read_text(encoding="utf-8")

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

                unwanted_fields = ['color', 'sequence', 'inherited_permission', 'access_token', 'document_token']
                # Removing unwanted fields
                for unwanted_field in unwanted_fields:
                    pattern_regular = rf'\s*<field name="{unwanted_field}">.*?</field>'
                    pattern_self_closing = rf'\s*<field name="{unwanted_field}"[^>]*\s*/>\s*'

                    content = re.sub(pattern_regular, "", content)
                    content = re.sub(pattern_self_closing, "", content)

                root_path = etree.fromstring(content.encode("utf-8"))

                for record in root_path.xpath("//record"):
                    model_name = record.get('model')
                    if not model_name:
                        continue

                    model = env.get(model_name)

                    if model is None:
                        continue
                    fields_set_in_record = {
                        field.get('name') for field in record.xpath('.//field')
                    }

                    for field_name in fields_set_in_record:
                        field_obj = model._fields.get(field_name)
                        if field_obj and field_obj.compute and field_obj.readonly:

                            pattern_standard = re.compile(
                                rf'\s*<field name="{field_name}">.*?</field>',
                                )
                            pattern_self_closing = re.compile(
                                    rf'\s*<field name="{field_name}"[^>]*\s*/>\s*'
                                )
                            content = pattern_standard.sub('', content)
                            content = pattern_self_closing.sub('', content)

                if file_name == "knowledge_article.xml":
                    content = re.compile('record id=.* model="knowledge.article"').sub('record id="welcome_article" model="knowledge.article"', content)
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
                    f.write(f"""    'assets': {{
        'web.assets_backend': [
            '{ind_name}/static/src/js/my_tour.js',
        ],
    }},
    'cloc_exclude': [
        'data/knowledge_article.xml',
        'static/src/js/my_tour.js',
    ],
    'images': ['images/main.png'],\n""")
                    f.write('}\n')
            elif not ext:
                shutil.copy(root + '/' + file_name, ind_name + current_dir + file_name)

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
                # Inject before </odoo>
                updated_content = content.replace("</odoo>", f"{new_function}\n</odoo>")
            else:
                # No closing tag — append new content and fix
                updated_content = content + "\n" + new_function + "\n</odoo>"
        else:
            # File doesn't exist — write base structure with function(s)
            updated_content = base_xml

        # Write back to file
        target_path.write_text(updated_content, encoding='utf-8')

    # Writing record in ascending order according to id
    path_ir_attachment_post = Path(ind_name + '/demo/' + 'ir_attachment_post.xml')
    if path_ir_attachment_post.exists():
        content_ir_attachment_post = path_ir_attachment_post.read_text(encoding='utf-8')
        root_ir_attchment_post = etree.fromstring(content_ir_attachment_post.encode("utf-8"))
        all_records = root_ir_attchment_post.xpath("//record")
        records = list(filter(lambda x: re.fullmatch(r'ir_attachment_\d+', x.get('id', '')), all_records))
        sorted_records = sorted(records, key = lambda x: int(x.get('id').split("_")[-1]))

        for record in records:
            root_ir_attchment_post.remove(record)
        for record in reversed(sorted_records):
            root_ir_attchment_post.insert(0, record)

        new_content_ir_attachment_post = etree.tostring(root_ir_attchment_post, pretty_print = True, encoding="utf-8", xml_declaration = True).decode("utf-8")
        path_ir_attachment_post.write_text(new_content_ir_attachment_post, encoding="utf-8")

    for file, content in mandatory_files.items():
        directory, _ = os.path.split(file)
        os.makedirs(ind_name + directory, exist_ok=True)
        Path(ind_name + file).write_text(content.format(ind_name=ind_name, Ind_name=Ind_name), encoding='utf-8')


if __name__ == "__main__":
    try:
        main()
    finally:
        cr.close()
