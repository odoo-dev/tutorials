from odoo import fields, models


class WarrantyConfiguration(models.Model):

    _name = "warranty.configuration"
    _description = "Warranty Configuration"

    name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one("product.product", string="Product_id")
    percentage = fields.Float(string="Percentage")
    period = fields.Integer(string="Period")
