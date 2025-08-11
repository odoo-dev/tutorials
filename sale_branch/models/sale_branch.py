from odoo import api, models, fields


class SaleBranch(models.Model):
    _name = 'sale.branch'
    _description = 'Sale Branch'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)

    sequence_id = fields.Many2one('ir.sequence', string='Sequence')

    @api.model_create_multi
    def create(self, vals_list):
        prepared = []
        for vals in vals_list:
            v = vals.copy()
            branch_name = v.get("name") or "Branch"
            branch_code = v.get("code") or "sale.branch"

            seq = self.env['ir.sequence'].create({
                'name': f'{branch_name}',
                'code': f'{branch_code}',
                "prefix": f"{branch_code.upper()}-",
                "padding": 4,
                "number_next": 1,
            })
            v['sequence_id'] = seq.id
            prepared.append(v)

        return super().create(prepared)
