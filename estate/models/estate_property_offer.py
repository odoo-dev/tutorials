from odoo import fields,models

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'real estate property offer'

    price= fields.Float()
    status= fields.Selection(
        selection=[
        ('accepted','Accepted'),
        ('Refused','Refused'),],
        copy=False
    )
    partner_id=fields.Many2one('res.partner',required=True)
    property_id=fields.Many2one('estate.property',required=True)
