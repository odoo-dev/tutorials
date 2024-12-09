from odoo import fields, models

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    warranty_id = fields.Many2one(
        comodel_name="sale.order.line",
        ondelete="cascade",
        string="parent sale order line",
    )