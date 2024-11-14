from odoo import fields, models
class EstatePeopertyOffer(models.Model):
    _name="estate.property.offer"
    _description="estate property offer model"
    price=fields.Float()
    status = fields.Selection(
        [('accepted', 'Accepted'),
        ('refused' , 'Refused')
        ],copy=False,)
    partner_id=fields.Many2one('res.partner')
    property_id=fields.Many2one('estate.property')