# frtan case study training

from odoo import fields, models, api
from odoo.orm.types import ValuesType

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one('sale.branch', string="Store Branch")

    @api.model
    def create(self, vals_list: list[ValuesType]):
        # print(vals_list)
        for vals in vals_list:
            sale_branch = self.env['sale.branch'].browse(vals['branch_id'])
            if sale_branch:
                sequence = sale_branch.sequence_id
                vals['name'] = self.env['ir.sequence'].next_by_code(sequence.prefix)
        result = super().create(vals_list)
        return result