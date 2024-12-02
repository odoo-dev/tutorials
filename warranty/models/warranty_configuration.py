from odoo import fields, models
class WarrantyConfiguration(models.Model):
    _name="warranty.configuration"
    _description="warranty congiguration"
    name=fields.Char(required=True)
    product=fields.Many2one('product.product',required=True)
    percentage=fields.Integer(required=True)
    year=fields.Integer(required=True)
