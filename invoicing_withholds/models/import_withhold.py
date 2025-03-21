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
    _rec_name = "description"

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
                    raise ValidationError(_("The uploaded file is not a valid Excel (.xls or .xlsx) file."))


    def process_withhold(self):
        for record in self:
            if not record.tax_file:
                raise UserError(_("No file is uploaded."))
            try:
                file_data = base64.b64decode(record.tax_file)
                self._process_xls_data(file_data)
                record.state = 'done'
            except Exception as e:
                self.env.cr.rollback()
                record.with_context(norecompute=True).write({'state': 'error'})
                self.env.cr.commit()
                raise UserError(_(f"Error processing file: {e}"))


    def _process_xls_data(self, file_data):
        try:
            file_stream = io.BytesIO(file_data)
            workbook = xlrd.open_workbook(file_contents=file_stream.read())
            withhold_dict = {}

            for sheet_index in range(workbook.nsheets):
                sheet = workbook.sheet_by_index(sheet_index)
                headers = {sheet.cell_value(0, col_idx).strip().lower(): col_idx for col_idx in range(sheet.ncols)}

                required_columns = ["number", "document number", "tax id"]
                missing_columns = [col for col in required_columns if col not in headers]
                if missing_columns:
                    raise ValidationError(_(f"Missing required columns: {', '.join(missing_columns)}"))

                for row_idx in range(1, sheet.nrows):
                    row = sheet.row(row_idx)
                    invoice_name = str(row[headers["number"]].value).strip()
                    document_number = str(row[headers["document number"]].value).strip()

                    try:
                        tax_id = int(float(row[headers["tax id"]].value))
                    except ValueError:
                        raise ValidationError(_(f"Invalid Tax ID at row {row_idx+1}"))

                    invoice = self.env['account.move'].search([
                        ('name', '=', invoice_name),
                        ('move_type', 'in', ['out_invoice', 'in_invoice']),
                        ('state', '=', 'posted')
                    ], limit=1)

                    if not invoice:
                        raise ValidationError(_(f"Invoice {invoice_name} does not exists or not in required type and state."))

                    partner = invoice.partner_id
                    try:
                        journal = int(row[headers['journal id']].value) if 'journal id' in headers else self.env['account.journal'].search([
                            ('company_id', '=', self.env.company.id),
                            ('l10n_ec_withhold_type', 'in', ['in_withhold', 'out_withhold'])
                        ], limit=1).id
                    except ValueError:
                        raise ValidationError(_(f"Invalid Journal Id at row {row_idx+1}"))
                    if not journal:
                        raise ValidationError(_(f"Invoice {invoice_name} does not have any valid journal."))

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

        except Exception as e:
            raise ValidationError(_(f"Error processing data: {e}"))


    def create_invoice_withhold(self, withhold_vals):
        invoice = withhold_vals.get('invoice_id')
        journal_id = withhold_vals.get('journal_id')
        document_number = withhold_vals.get('document_number')

        wizard = self.env['l10n_ec.wizard.account.withhold'].with_context(
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

        res = wizard.action_create_and_post_withhold()

        if res:
            invoice_link = invoice._get_html_link(title=invoice.name)
            content = _('Withhold has been generated for %(invoice_link)s.', invoice_link=invoice_link)
            body = Markup('<p>%s</p>') % content
            res.message_post(
                body=body, subtype_xmlid="mail.mt_note"
            )

        return res
