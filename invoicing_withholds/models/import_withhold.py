import io
import os
import xlrd
import base64
from markupsafe import Markup
from odoo import _, api, Command, fields, models
from odoo.exceptions import UserError, ValidationError

class ImportWithhold(models.Model):
    _name = "import.withhold"
    _description = "imports withhold from xls files"

    description = fields.Char(string="Description", help="Enter a brief description of the withhold import.")
    tax_file = fields.Binary(string="Tax File", help="Upload the tax file in XLS format,\n please include invoice name and tax id in file.")
    file_name = fields.Char(string="File Name")
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('done', 'Done'),
            ('error', 'Error')
        ],
        default='new'
    )


    @api.constrains('file_name', 'tax_file')
    def _check_file_extension(self):
        for record in self:
            if record.file_name:
                extension = os.path.splitext(record.file_name)[1].lower()
                if extension not in ['.xls', '.xlsx']:
                    raise ValidationError("The uploaded file is not a valid Excel (.xls or .xlsx) file.")


    def process_withhold(self):
        for record in self:
            if not record.tax_file:
                raise UserError("No file is uploaded.")
            file_data = base64.b64decode(record.tax_file)
            self._process_xls_data(file_data)


    def _process_xls_data(self, file_data):
        file_stream = io.BytesIO(file_data)
        try:
            workbook = xlrd.open_workbook(file_contents=file_stream.read())
        except xlrd.XLRDError:
            raise ValidationError("Invalid Excel file format. Please upload a valid .xls file.")

        sheet = workbook.sheet_by_index(0)
        headers = {sheet.cell_value(0, col_idx).strip(): col_idx for col_idx in range(sheet.ncols)}
        required_columns = ["Number", "Document Number", "Tax Id"]
        missing_columns = [col for col in required_columns if col not in headers]

        if missing_columns:
            raise ValidationError(f"Missing required columns: {', '.join(missing_columns)}")

        withhold_dict = {}
        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            invoice_name = str(row[headers["Number"]].value).strip()
            document_number = str(row[headers["Document Number"]].value).strip()

            try:
                tax_id = int(float(row[headers["Tax Id"]].value))
            except ValueError:
                raise ValidationError(f"Invalid Tax ID at row {row_idx+1}")

            invoice = self.env['account.move'].search([
                ('name', '=', invoice_name),
                ('move_type', 'in', ['out_invoice', 'in_invoice']),
                ('state', '=', 'posted')
            ], limit=1)

            if not invoice:
                raise ValidationError(f"Invoice not found: {invoice_name}")

            partner = invoice.partner_id
            journal = invoice.journal_id or self.env['account.journal'].search([
                ('company_id', '=', self.env.company.id),
                ('type', '=', 'general')
            ], limit=1)

            invoice_id = invoice.id
            if invoice_id in withhold_dict:
                withhold_dict[invoice_id]['tax_ids'].append(tax_id)
            else:
                withhold_dict[invoice_id] = {
                    'invoice_id': invoice,
                    'partner_id': partner,
                    'journal_id': journal,
                    'document_number': document_number,
                    'tax_ids': [tax_id],
                }

        for withhold in withhold_dict.values():
            self.create_invoice_withhold(withhold)


    def create_invoice_withhold(self, withhold_vals):
        invoice = withhold_vals.get('invoice_id')

        if not invoice:
            raise UserError(f"Invoice not found: {withhold_vals.get('invoice_id').name}")

        journal_id = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('type', '=', 'general')
            ], limit=1).id

        document_number = withhold_vals.get('document_number')
        
        tds_wizard = self.env['l10n_ec.wizard.account.withhold'].with_context(
            active_model='account.move', active_ids=invoice.ids
        ).create({
            'journal_id': journal_id,
            'date': invoice.invoice_date,
            'document_number': document_number,
            'withhold_line_ids': [
                Command.create({
                    'invoice_id': invoice.id,
                    'tax_id': tax_id,
                    'base': invoice.amount_total
                }) for tax_id in withhold_vals["tax_ids"]
            ]
        })

        res = tds_wizard.action_create_and_post_withhold()

        if res:
            invoice_link = invoice._get_html_link(title=invoice.name)
            content = _('Withhold has been generated for %(invoice_link)s.', invoice_link=invoice_link)
            body = Markup('<p>%s</p>') % content
            res.message_post(
                body=body, subtype_xmlid="mail.mt_note"
            )

        return res
