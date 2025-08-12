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
                    'prefix': f"{val['code']}/",
                }
                sequence = self.env['ir.sequence'].create(sequence_vals)
                val['sequence_id'] = sequence.id
            else:
                raise ValueError("Both 'name' and 'code' must be provided to create a Sale Branch.")
        return super().create(vals)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name and self.code:
            self.sequence_id.name = f"{self.name} - {self.code}"

    @api.onchange('code')
    def _onchange_code(self):
        if self.name and self.code:
            self.sequence_id.name = f"{self.name} - {self.code}"
            self.sequence_id.code = f"sale.branch.{self.code}"
            self.sequence_id.prefix = f"{self.code}/"
