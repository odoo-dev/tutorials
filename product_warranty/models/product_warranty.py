from odoo import fields, models


class ProductWarranty(models.Model):
    _name = 'product.warranty'
    _description = 'warranty in product'

    name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one('product.product', string="Product", required=True)
    percentage = fields.Float(string="Percentage", required=True)
