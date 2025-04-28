from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    custom_image = fields.Boolean(string="Custom Image", default=False)
