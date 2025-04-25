from odoo import fields, models


class EstatePropertyOfferModel(models.Model):
    _name = "estate_property_offer"
    _description = "Estate property offer"

    price = fields.Float()
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate_property", required=True)
