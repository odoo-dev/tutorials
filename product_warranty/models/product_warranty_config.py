from odoo import api, fields, models


class ProductWarrantyConfig(models.Model):
    _name = 'product.warranty.config'
    _description = "Product warranty configuration"

    name = fields.Char(string="Warranty Period", required=True)
    product_tmpl_id = fields.Many2one('product.template', string="Product", required=True)
    percentage = fields.Float(string="Percentage", required=True)
