from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    custom_image = fields.Binary("Custom Image")
    # custom_image = fields.Binary("Custom Image", attachment=True)
