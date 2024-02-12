from odoo import fields, models

class estatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"

    price = fields.Float()
    status = fields.Selection(
        string='State',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy=False,
    )
    partner_id = fields.Many2one('res.partner')
    property_id = fields.Many2one('estate.property')
