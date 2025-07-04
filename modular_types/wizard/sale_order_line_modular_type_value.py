from odoo import models, fields


class SaleOrderLineModularTypeValue(models.Model):
    _name = "sale.order.line.modular.type.value"

    sale_order_line_id = fields.Many2one(
        "sale.order.line", required=True, ondelete="cascade"
    )
    modular_type_id = fields.Many2one("modular.type", required=True, ondelete="cascade")
    value = fields.Integer(string="Value", required=True)
