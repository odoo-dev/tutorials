from odoo import models, fields, api


class SaleBranch(models.Model):
    _name = 'sale.branch'
    _description = 'Sale Branch'

    name = fields.Char(string='Branch Name', required=True)
    code = fields.Char(string='Branch Code', required=True, copy=False)
    sequence_id = fields.Many2one(comodel_name='ir.sequence', string='Sequence')

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if 'name' in val and 'code' in val:
                sequence_vals = {
                    'name': f"{val['name']} - {val['code']}",
                    'code': f"sale.branch.{val['code']}",
                }
                sequence = self.env['ir.sequence'].create(sequence_vals)
                val['sequence_id'] = sequence.id
            else:
                raise ValueError("Both 'name' and 'code' must be provided to create a Sale Branch.")
        return super().create(vals)
