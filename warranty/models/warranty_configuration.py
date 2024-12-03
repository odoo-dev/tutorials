from odoo import fields, models
class WarrantyConfiguration(models.Model):
    _name="warranty.configuration"
    _description="warranty congiguration"
    name=fields.Char(required=True)
    product_id=fields.Many2one('product.product',required=True)
    percentage=fields.Integer(required=True)
    year=fields.Integer(required=True)
    # end_date=fields.Date(compute=(_compute_warranty_end_date),readonly=True)

    # @api.depends("year")
    # def _compute_warranty_end_date(self):
    #     for record in self:



