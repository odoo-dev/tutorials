from odoo import api, fields, models, Command


class EstateProperty(models.Model):
    _inherit = "sale.order"

    branch_id = fields.Many2one("sale.branch", string="Branch")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('branch_id'):
                branch = self.env['sale.branch'].browse(vals['branch_id'])
                vals['name'] = branch.sequence_id.next_by_id()

        return super(EstateProperty, self).create(vals)
