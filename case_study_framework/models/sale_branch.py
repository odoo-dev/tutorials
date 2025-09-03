from odoo import fields, models, api

class SaleBranch(models.Model):
    _name = "sale.branch"
    _description = "Sale Branch"

    name = fields.Char("Branch Name", required=True)
    code = fields.Char("Branch Code", required=True)
    sequence_id = fields.Many2one("ir.sequence", string="Sequence")

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            seq_vals = {
                'name': f"{val['name']} Sequence",
                'code': f"{val['code']}",
                'prefix': f"S{val['code'].upper()}",
                'padding': 4,
                'number_increment': 1,
            }
            seq = self.env['ir.sequence'].create(seq_vals)
            val['sequence_id'] = seq.id
        return super(SaleBranch, self).create(vals)
