import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from lxml import etree
from pathlib import Path

from script import (
    check_command,
    setup_odoo_env,
    get_etree_content,
    write_etree_content,
    remove_computed_fields,
    remove_unwanted_fields,
    remove_model_based_fields,
    unorder_manifest_demo_files,
    get_scss_content,
)

class TestClass(unittest.TestCase):

    def setUp(self):
        self.current_dir = '/some/module/demo/'
        self.file_name = 'demo_file.xml'
        self.xml_content = """<?xml version='1.0' encoding='UTF-8'?>
<record id="rec_1" model="sale.order">
    <field name="computed_field" ref="base_module.res_partner_26"/>
</record>
"""
        self.etree_content = etree.fromstring(self.xml_content.encode('utf-8'))

    @patch('os.path.isdir', return_value=False)
    def test_check_command(self, mock_isdir):
        test_args = ['script.py', '-d', 'test_db', '-m', 'test_module', '-c', 'test_category', '-p', 'some_path']
        with patch.object(sys, 'argv', test_args):
            result = check_command(sys.argv)
            self.assertEqual(result, ('test_module', 'test_category', 'test_db', 'some_path'))

    @patch('os.path.isdir', return_value=False)
    def test_invalid_command(self, mock_isdir):
        test_args = ['script.py', '-m', 'test_module', '-c', 'test_category']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                check_command(sys.argv)

    @patch('os.path.isdir', return_value=True)
    def test_module_exist(self, mock_isdir):
        test_args = ['script.py', '-d', 'test_db', '-m', 'test_module', '-c', 'test_category', '-p', 'some_path']
        with patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit):
                check_command(sys.argv)

    @patch('os.path.isdir', return_value=True)
    def test_module_exist_with_force(self, mock_isdir):
        test_args = ['script.py', '-d', 'test_db', '-m', 'test_module', '-c', 'test_category', '-p', 'some_path', 'force']
        with patch.object(sys, 'argv', test_args):
            result = check_command(sys.argv)
            self.assertEqual(result, ('test_module', 'test_category', 'test_db', 'some_path'))

    @patch('script.api.Environment')
    @patch('script.odoo.sql_db.db_connect')
    @patch('script.odoo.modules.registry.Registry.new')
    @patch('script.odoo.tools.config', {})
    @patch('script.SUPERUSER_ID', 1)
    def test_setup_odoo_env(self, mock_registry_new, mock_db_connect, mock_env):

        mock_registry = MagicMock()
        mock_cursor = MagicMock()
        mock_env_instance = MagicMock()

        mock_registry_new.return_value = mock_registry
        mock_registry.setup_signaling.return_value = None
        mock_db_connect.return_value.cursor.return_value = mock_cursor
        mock_env.return_value = mock_env_instance

        cr, env = setup_odoo_env('test_db')

        self.assertEqual(cr, mock_cursor)
        self.assertEqual(env, mock_env_instance)

    @patch('script.odoo.tools.config', {})
    @patch('script.SUPERUSER_ID', 1)
    def test_setup_odoo_env_exception(self):
        with self.assertRaises(SystemExit) as cm:
            setup_odoo_env("test_db")

    def test_get_etree_content(self):
        mock_path = MagicMock()
        mock_path.read_text.return_value = self.xml_content
        result = get_etree_content(mock_path)

        self.assertIsInstance(result, etree._Element)
        self.assertEqual(result.tag, 'record')
        self.assertEqual(result[0].tag, 'field')

    def test_get_etree_content_exception(self):
        mock_path = MagicMock()
        mock_path.read_text.return_value = "<xml>Error xml"

        with self.assertRaises(Exception) as cm:
            get_etree_content(mock_path)

    def test_write_etree_content(self):
        mock_path = MagicMock()
        write_etree_content(mock_path, self.etree_content)

        mock_path.write_text.assert_called_once_with(self.xml_content, encoding="utf-8")

    def test_write_etree_content_exception(self):
        mock_path = MagicMock()
        mock_path.write_text.side_effect = Exception("Error while writing etree")
        with self.assertRaises(Exception) as cm:
            write_etree_content(mock_path, self.etree_content)

    def test_remove_computed_fields(self):
        xml_content = """
            <odoo noupdate="1">
                <record id="sale_order_15">
                    <field name="computed_field" ref="base_module.res_partner_26"/>
                    <field name="notreadonly_field"></field>
                    <field name="normal_field"></field>
                    <field name="computed_field_2"></field>
                    <field name="one_2_many_field"></field>
                    <field name="normal_field_2"></field>
                    <field name="many_2_many_field"></field>
                </record>
            </odoo>
        """
        etree_content = etree.fromstring(xml_content.encode("utf-8"))
        mock_env = MagicMock()
        mock_model = MagicMock()
        mock_env.get.return_value = mock_model

        computed_field = MagicMock(compute=True, readonly=True, type='char')
        notreadonly_field = MagicMock(compute=True, readonly=False, type='char')
        normal_field = MagicMock(compute=False, readonly=False, type='char')
        computed_field_2 = MagicMock(compute=True, readonly=True, type='char')
        normal_field_2 = MagicMock(compute=False, readonly=True, type='char')

        mock_model._fields = {
            'computed_field': computed_field,
            'computed_field_2': computed_field_2,
            'normal_field': normal_field,
            'normal_field_2': normal_field_2,
            'notreadonly_field': notreadonly_field,
        }

        cleaned_content = remove_computed_fields(mock_env, 'some.model', etree_content, xml_content)

        self.assertIn('normal_field', cleaned_content)
        self.assertIn('normal_field_2', cleaned_content)
        self.assertIn('notreadonly_field', cleaned_content)
        self.assertNotIn('computed_field', cleaned_content)
        self.assertNotIn('computed_field_2', cleaned_content)

    def test_remove_computed_fields_if_model_not_found(self):
        mock_env = MagicMock()
        mock_env.get.return_value = None

        result = remove_computed_fields(mock_env, 'some.model', self.etree_content, self.xml_content)
        self.assertEqual(self.xml_content, result)

    def test_remove_unwanted_fields(self):
        xml_content = """
            <odoo>
                <record id="sale_order_15" model="sale.order">
                    <field name="wanted" ref="base_module.res_partner_26"/>
                    <field name="unwanted"></field>
                    <field name="not_needed"></field>
                </record>
            </odoo>
        """
        unwanted_fields = ['unwanted', 'not_needed']
        cleaned_content = remove_unwanted_fields(xml_content, unwanted_fields)

        self.assertIn('wanted', cleaned_content)
        self.assertNotIn('unwanted', cleaned_content)
        self.assertNotIn('not_needed', cleaned_content)

    def test_remove_model_based_fields(self):
        xml_content = """
        <odoo>
            <record id="crm_lead_5" model="crm.lead">
                <field name="partner_id" ref="base_module.res_partner_26"/>
                <field name="country_id" ref="base.be"/>
                <field name="name">John Smith's opportunity</field>
                <field name="user_id" ref="base.user_admin"/>
                <field name="team_id" ref="sales_team.team_sales_department"/>
                <field name="company_id" ref="base.main_company"/>
                <field name="stage_id" ref="crm.stage_lead1"/>
                <field name="tag_ids" eval="[(6, 0, [ref('crm_tag_4')])]"/>
                <field name="email_from">john.smith@fifth.example.com</field>
                <field name="email_state">correct</field>
                <field name="date_open">2025-02-10 12:14:35</field>
                <field name="contact_name">John Smith</field>
                <field name="partner_name">Fifth Company</field>
                <field name="email_domain_criterion">@fifth.example.com</field>
                <field name="street">Rue Paul Reuter 8</field>
                <field name="zip">6700</field>
                <field name="city">Arlon</field>
                <field name="won_status">pending</field>
                <field name="reveal_id">b30f51bb-e876-4dc7-aa71-46c7a4f7b9bf</field>
                <field name="iap_enrich_done" eval="True"/>
            </record>
            <record id="crm_lead_4" model="crm.lead">
                <field name="partner_id" ref="base_module.res_partner_28"/>
                <field name="country_id" ref="base.be"/>
                <field name="name">Mike Brown's opportunity</field>
                <field name="user_id" ref="base.user_admin"/>
                <field name="team_id" ref="sales_team.team_sales_department"/>
                <field name="company_id" ref="base.main_company"/>
                <field name="stage_id" ref="crm.stage_lead4"/>
                <field name="tag_ids" eval="[(6, 0, [ref('crm_tag_2')])]"/>
                <field name="email_from">mike.brown@b2c.example.com</field>
                <field name="email_state">correct</field>
                <field name="probability">100.0</field>
                <field name="date_open">2025-02-10 12:05:36</field>
                <field name="contact_name">Mike Brown</field>
                <field name="email_domain_criterion">@b2c.example.com</field>
                <field name="street">Rue Brederode 16</field>
                <field name="zip">1000</field>
                <field name="city">Bruxelles</field>
                <field name="won_status">won</field>
            </record>
        </odoo>
        """
        cleaned_content = remove_model_based_fields('crm.lead', xml_content)
        crm_unwanted_field = ['email_from', 'company_id', 'country_id', 'city', 'street', 'partner_name', 'contact_name', 'zip', 'reveal_id']
        for field in crm_unwanted_field:
            self.assertNotIn(field, cleaned_content)

    def test_unorder_manifest_demo_files_insert_before_match(self):
        manifest_demo_file_list = [{'file_name': 'existing_file.xml', 'ref_name': ['rec_1']}]
        ref_name_list = ['new_ref']

        unorder_manifest_demo_files(manifest_demo_file_list, self.current_dir, self.file_name, ref_name_list, self.etree_content)
        self.assertEqual(len(manifest_demo_file_list), 2)
        self.assertEqual(manifest_demo_file_list[0]['file_name'], 'demo_file.xml')
        self.assertEqual(manifest_demo_file_list[1]['file_name'], 'existing_file.xml')

    def test_unorder_manifest_demo_files_insert_at_end_if_no_match(self):
        manifest_demo_file_list = [{'file_name': 'existing_file.xml', 'ref_name': ['non']}]
        ref_name_list = ['new_ref']
        unorder_manifest_demo_files(manifest_demo_file_list, self.current_dir, self.file_name, ref_name_list, self.etree_content)

        self.assertEqual(len(manifest_demo_file_list), 2)
        self.assertEqual(manifest_demo_file_list[0]['file_name'], 'existing_file.xml')
        self.assertEqual(manifest_demo_file_list[1]['file_name'], 'demo_file.xml')

    def test_unorder_manifest_demo_files_insert_at_start_if_no_ref_list(self):
        manifest_demo_file_list = [{'file_name': 'existing_file.xml', 'ref_name': ['non']}]
        ref_name_list = []
        unorder_manifest_demo_files(manifest_demo_file_list, self.current_dir, self.file_name, ref_name_list, self.etree_content)

        self.assertEqual(len(manifest_demo_file_list), 2)
        self.assertEqual(manifest_demo_file_list[0]['file_name'], 'demo_file.xml')
        self.assertEqual(manifest_demo_file_list[1]['file_name'], 'existing_file.xml')

    def test_unorder_manifest_demo_files_skip_if_folder_not_demo(self):
        current_dir = 'some/module/data/'
        manifest_demo_file_list = [{'file_name': 'existing_file.xml', 'ref_name': ['rec_1']}]
        ref_name_list = ['new_ref']

        unorder_manifest_demo_files(manifest_demo_file_list, current_dir, self.file_name, ref_name_list, self.etree_content)

        self.assertEqual(len(manifest_demo_file_list), 1)
        self.assertEqual(manifest_demo_file_list[0]['file_name'], 'existing_file.xml')

    @patch('script.Path.read_text')
    def test_get_scss_content_with_match_and_color_file(self, mock_read_text):
        mock_scss = """
        $o-user-color-palette: map-merge($o-user-color-palette, o-map-omit((
            'o-color-1': #000000,
            'menu': 'NULL',
            'menu-custom': 'white',
            'o-cc1-btn-primary': #57B4BA,
            // -- hook --
        )));
        """
        mock_read_text.return_value = mock_scss

        scss_list = []
        root = '/some_path/path'
        file_name = 'user_color_palette.scss'

        get_scss_content(scss_list, root, file_name)

        self.assertEqual(len(scss_list), 1)
        self.assertIn('inner_scss_content', scss_list[0])
        self.assertIn("'o-color-1'", scss_list[0]['inner_scss_content'])
        self.assertEqual(scss_list[0]['url'], '/website/static/src/scss/options/colors/user_color_palette.scss')

    @patch('script.Path.read_text')
    def test_get_scss_content_with_match_and_other_file(self, mock_read_text):
        mock_scss = """
        $o-user-website-values: map-merge($o-user-website-values, o-map-omit((
            'menu-gradient': 'NULL',
            'menu-secondary-gradient': null,
            'footer-gradient': null,
            'copyright-gradient': null,
        )));
        """
        mock_read_text.return_value = mock_scss

        scss_list = []
        root = '/some_path/path'
        file_name = 'user_palette.scss'

        get_scss_content(scss_list, root, file_name)
        self.assertEqual(len(scss_list), 1)
        self.assertIn('inner_scss_content', scss_list[0])
        self.assertIn("'menu-gradient'", scss_list[0]['inner_scss_content'])
        self.assertEqual(scss_list[0]['url'], '/website/static/src/scss/options/user_palette.scss')
    
    @patch('script.Path.read_text')
    def test_get_scss_content_with_no_match(self, mock_read_text):
        mock_read_text.return_value = "$no-match: some-value();"
        scss_list = []
        root = '/some/path'
        file_name = 'no_match.scss'

        get_scss_content(scss_list, root, file_name)

        self.assertEqual(scss_list, []) 


if __name__ == '__main__':
    unittest.main()
