from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_image = fields.Binary(string="Custom Image")
