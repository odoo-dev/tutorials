from odoo import fields, models

class EstatePropertyTags(models.Model):
    _name = "estate.property.offer"
    _description = "Model for Real Estate Property Offers"

    price = fields.Float(string = "Price")
    status = fields.Selection([('accepted', 'Accepted'),('refused', 'Refused')], string='Status',copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
