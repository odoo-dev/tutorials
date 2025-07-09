from odoo import api,fields, models

class SaleOrderInherited(models.Model):
    _inherit = "sale.order"

    branch_id = fields.Many2one("sale.branch", string="Branch ID")

    @api.model
    def create(self, vals):
        # For debugging purpose
        # print(vals)
        # print(vals["branch_id"])
        # print(self.env['sale.branch'].browse(vals['branch_id']))
        # print(self.env['sale.branch'].browse(vals['branch_id']).name)
        # print(self.env['sale.branch'].browse(vals['branch_id']).code)
        # print(self.env['sale.branch'].browse(vals['branch_id']).sequence_id)
        if vals["branch_id"]:
            branch = self.env['sale.branch'].browse(vals['branch_id'])
            vals["name"] = branch.sequence_id.next_by_id()

        return super().create(vals)

