from odoo import models, fields
from dateutil.relativedelta import relativedelta
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property data model"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=fields.Date.today()+ relativedelta(month=3),copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[('n', 'North'), 
                   ('s', 'South'),
                   ('e', 'East'),
                   ('w', 'West'),
                   ],
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(selection=[
        ('new','New'),
        ('offer_received','Offer Received'),
        ('offer_accepted','Offer Accepted'),
        ('sold','Sold'),
        ('cancelled','Cancelled'),
    ],
        default = 'new',
        copy = False
    )

