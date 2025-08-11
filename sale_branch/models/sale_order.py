from odoo import api, models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one('sale.branch', string='Branch')

    @api.model_create_multi
    def create(self, vals_list):
        prepared = []
        for vals in vals_list:
            v = vals.copy()

            branch_id = v.get("branch_id")

            if branch_id:
                branch = self.env['sale.branch'].browse(int(branch_id))

                if not branch.exists():
                    raise UserError('Branch does not exist')
                if not branch.sequence_id:
                    raise UserError('Branch sequence does not exist')

                seq_name = branch.sequence_id.next_by_id()
                v['name'] = seq_name

            prepared.append(v)

        return super().create(prepared)
