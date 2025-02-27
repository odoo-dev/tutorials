from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_warranty = fields.Boolean(string="Is Warranty Available")
    warranty_ids = fields.One2many('product.warranty.config', 'product_tmpl_id', string="Warranty options")
