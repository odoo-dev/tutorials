from odoo import api, models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    custom_image = fields.Binary("Custom Image", attachment=True)
    # custom_image_base64 = fields.Text()
