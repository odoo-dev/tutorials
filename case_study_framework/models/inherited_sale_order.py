from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one(
        comodel_name='sale.branch',
        string='Branch',
        required=True
    )

    @api.model_create_multi
    def create(self, val_list):
        for vals in val_list:
            if 'branch_id' in vals:
                branch = self.env['sale.branch'].browse(vals['branch_id'])
                if branch and branch.sequence_id:
                    vals['name'] = branch.sequence_id.next_by_id()
                else:
                    raise ValueError("Branch must have a sequence defined.")
            else:
                raise ValueError("Branch ID must be provided to create a Sale Order.")
        return super().create(val_list)
