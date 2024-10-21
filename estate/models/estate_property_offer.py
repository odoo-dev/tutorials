from odoo import fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate properties offer"

    price = fields.Float(string="Price")
    status = fields.Selection(
        string='Status',
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        help="Offer status",
        copy=False)
    partner_id = fields.Many2one('res.partner', string='Offerer', required=True)
    property_id = fields.Many2one('estate.property', required=True)
