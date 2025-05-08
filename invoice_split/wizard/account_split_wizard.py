# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, Command, fields, models
from odoo.exceptions import UserError


class AccountSplitWizard(models.TransientModel):
    _name = 'account.split.wizard'
    _description = 'Split Invoice Wizard'

    split_no = fields.Integer(
        string="Split into",
        help="Specify how many separate invoices you want to create by splitting the original invoice."
    )
    parent_line_ids = fields.One2many(
        comodel_name='account.split.move.wizard',
        inverse_name='parent_wizard_id',
        string="Parent Lines",
    )
    child_line_ids = fields.One2many(
        comodel_name='account.split.move.wizard',
        inverse_name='child_wizard_id',
        string="Child Lines",
    )
    source_invoice_id = fields.Many2one(
        comodel_name='account.move',
        string="Source Invoice"
    )

    def action_generate_split(self):
        self.ensure_one()

        invoice = self.env['account.move'].browse(self.env.context['active_ids'])

        max_qty = max(invoice.invoice_line_ids.mapped('quantity'))
        if (self.split_no <= 1 or self.split_no > max_qty):
            raise UserError("Invalid split number: Please enter a number greater than 1 and less than or equal to the maximum quantity of any invoice line.")

        parent_lines = []
        grouped_invoice = {i: [] for i in range(1, self.split_no + 1)}
        for line in invoice.invoice_line_ids:
            parent_lines.append(self._prepare_split_line_vals(line, is_parent=True))
            quantities = self._distribute_quantity(line.quantity, self.split_no)
            for i, qty in enumerate(quantities):
                if qty > 0:
                    grouped_invoice[i + 1].append(self._prepare_split_line_vals(line, invoice=invoice, qty=qty, index=i + 1))

        child_invoice_line = []
        for key, value in grouped_invoice.items():
            child_invoice_line.append(Command.create({
                        'name': f"Invoice {key}",
                        'display_type': "line_section"
                    }))
            for _, _, data in value:
                child_invoice_line.append(Command.create(data))

        self.write({
            'parent_line_ids': parent_lines,
            'child_line_ids': child_invoice_line,
            'source_invoice_id': invoice.id
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Journal Entry Wizard',
            'res_model': 'account.split.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('invoice_split.account_split_move_wizard_form_view').id,
            'target': 'new',
        }

    def _distribute_quantity(self, total_qty, splits):
        base = total_qty // splits
        remainder = total_qty % splits
        result = [base + 1 if i < remainder else base for i in range(splits)]
        return result

    def _prepare_split_line_vals(self, line, invoice=None, qty=None, index=None, is_parent=False):
        quantity = qty if qty is not None else line.quantity
        if is_parent:
            subtotal = line.price_subtotal
            tax_amount = line.price_total - line.price_subtotal
            total = line.price_total
        else:
            taxes = line.tax_ids.compute_all(
                line.price_unit,
                currency=invoice.currency_id if invoice else False,
                quantity=qty,
                product=line.product_id,
                partner=invoice.partner_id if invoice else False
            )
            subtotal = taxes['total_excluded']
            tax_amount = taxes['total_included'] - taxes['total_excluded']
            total = taxes['total_included']
        vals = {
            'product_id': line.product_id.id,
            'name': line.name,
            'price': line.price_unit,
            'quantity': quantity,
            'tax': [(6, 0, line.tax_ids.ids)],
            'subtotal': subtotal,
            'untaxed_amount': subtotal,
            'tax_amount': tax_amount,
            'total': total,
            'is_parent_invoice': is_parent,
        }
        if not is_parent and index is not None:
            vals['invoice_index'] = index

        return Command.create(vals)

    def action_create_split_invoices(self):
        self.ensure_one()

        invoice = self.source_invoice_id
        current_invoice = None
        invoice_data = invoice.copy_data()[0]
        name = invoice.name

        for line in self.child_line_ids:
            if (line.display_type == 'line_section'):
                if (line.name == "Invoice 1"):
                    current_invoice = invoice
                    current_invoice.name = f"{name}/{line.name}"
                else:
                    invoice_data.update({
                        'name': f"{name}/{line.name}" if name else line.name,
                    })
                    current_invoice = self.env['account.move'].create(invoice_data)
                current_invoice.invoice_line_ids.unlink()

                self.env['account.move.line'].create({
                    'name': line.name,
                    'display_type': "line_section",
                    'move_id': current_invoice.id,
                })
            else:
                vals = {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'quantity': line.quantity,
                    'tax_ids': [(6, 0, line.tax.ids)] if line.tax else [],
                    'move_id': current_invoice.id if current_invoice else False
                }
                self.env['account.move.line'].create(vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('move_type', '=', 'out_invoice')],
            'view_mode': 'tree,form',
            'target': 'current',
        }
