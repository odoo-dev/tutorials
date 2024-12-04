from odoo import fields, models
class WarrantyConfiguration(models.Model):
    _name="warranty.configuration"
    _description="warranty congiguration"
    name=fields.Char(required=True)
    product_id=fields.Many2one('product.product',required=True, string="product")
    percentage=fields.Float(required=True, default=0.0)
    year=fields.Integer(required=True)
