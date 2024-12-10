from odoo import fields, models,Command


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    warranty_sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        ondelete="cascade",
        string="parent sale order line",
    )

    # def action_remove_all(self):
    #     self.order_id.write({'order_line':[Command.clear()]})
