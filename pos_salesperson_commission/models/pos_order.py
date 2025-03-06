from odoo import models, fields
# from odoo.exceptions import User


class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('res.user_ids', string='Salesperson', help="Salesperson associated with the order")

    def _process_commision_lines(self, pos_order):
        if pos_order.salesperson_id:
            existing_commision = self.env["pos.salesperson.commission"].search([("user_id", "=", pos_order.salesperson_id.id)])
            if existing_commision:
                existing_commision.write({'order_ids': [4, pos_order.id]})
            else:
                breakpoint()
                self.env["pos.salesperson.commission"].create({
                    # "salesperson_id": pos_order.sales_person_id.id,
                    "order_ids": [4, pos_order.id],
                })
        return pos_order