from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_custom_image = fields.Boolean(string="Allow Image Uploads", default=True)
