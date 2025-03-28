import base64
from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError

@tagged('post-install', '-at-install')
class TestCreateInvoiceWithhold(TransactionCase):

    def setUp(self):
        super().setUp()

        self.journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'type': 'purchase',
            'code': 'TEST',
            'company_id': 2,
        })
        self.tax = self.env['account.tax'].create({
            'name': 'Test Tax',
            'amount': 10.0,
            'type_tax_use': 'purchase',
            'company_id': 2,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
        })
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'service',
            'list_price': 100.0,
        })
        self.partner = self.env.ref('base.res_partner_1')
        self.partner.write({
            'l10n_latam_identification_type_id': self.env.ref('l10n_ec.ec_ruc').id,
            'vat': '0999999999001'
        })
        self.payment_method = self.env['l10n_ec.sri.payment'].create({
            'name': 'Credit Card',
            'code': 'CC'
        })
        self.invoice = self.env['account.move'].create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice',
            'partner_id': self.partner.id,
            'journal_id': self.journal.id,
            'l10n_ec_sri_payment_id': self.payment_method.id,
            'amount_total': 100.0,
            'journal_id': 8,
            'invoice_line_ids': [
                Command.create({
                    'product_id': self.product.id,
                    'name': 'Test Product Line',
                    'quantity': 1,
                    'price_unit': 100.0,
                })
            ]
        })
        self.invoice.action_post()


    def test_process_withhold_no_file(self):
        withhold_record = self.env['import.withhold'].create({
            'description': 'No File Test',
            'file_name': 'withhold.xls',
            'tax_file': False
        })

        with self.assertRaises(UserError, msg="No file is uploaded."):
            withhold_record.process_withhold()

    def test_valid_file_extension_xls(self):
        valid_record = self.env['import.withhold'].create({
            'description': 'Valid XLS Test',
            'file_name': 'test_file.xls',
            'tax_file': base64.b64encode(b'Test content')
        })
        self.assertTrue(valid_record, "Valid .xls file should be accepted.")

    def test_valid_file_extension_xlsx(self):
        valid_record = self.env['import.withhold'].create({
            'description': 'Valid XLSX Test',
            'file_name': 'test_file.xlsx',
            'tax_file': base64.b64encode(b'Test content')
        })
        self.assertTrue(valid_record, "Valid .xlsx file should be accepted.")

    def test_invalid_file_extension_pdf(self):
        with self.assertRaises(ValidationError, msg="The uploaded file is not a valid Excel (.xls or .xlsx) file."):
            self.env['import.withhold'].create({
                'description': 'Invalid PDF Test',
                'file_name': 'test_file.pdf',
                'tax_file': base64.b64encode(b'Test content')
            })

    def test_create_invoice_withhold_success(self):
        withhold_vals = {
            'invoice_id': self.invoice,
            'journal_id': self.journal.id,
            'document_number': '001-002-000000123',
            'tax_ids': [self.tax.id],
        }
        withhold_model = self.env['import.withhold']
        res = withhold_model.create_invoice_withhold(withhold_vals)
        self.assertTrue(res, "Withhold creation should return a valid response.")

    def test_create_invoice_withhold_missing_invoice(self):
        withhold_vals = {
            'invoice_id': False,
            'journal_id': self.journal.id,
            'document_number': '001-002-000000123',
            'tax_ids': [self.tax.id],
        }
        withhold_model = self.env['import.withhold']
        with self.assertRaises(AttributeError):
            withhold_model.create_invoice_withhold(withhold_vals)

    def test_create_invoice_withhold_no_tax_ids(self):
        withhold_vals = {
            'invoice_id': self.invoice,
            'journal_id': self.journal.id,
            'document_number': '001-002-000000123',
            'tax_ids': [],
        }
        withhold_model = self.env['import.withhold']
        with self.assertRaises(ValidationError) as context:
            withhold_model.create_invoice_withhold(withhold_vals)

        self.assertIn("You must input at least one withhold line", str(context.exception))
