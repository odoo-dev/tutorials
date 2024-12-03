from odoo import fields,models
class ProductTemplate(models.Model):
    _inherit = "product.template"
    warranty=fields.Boolean(String ="is warranty require ?")