from odoo import fields, models
from dateutil.relativedelta import relativedelta

class estateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property Model"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode= fields.Char()
    date_availability=fields.Date(copy=False, default=fields.Date.today()+relativedelta(months=3))
    expected_price=fields.Float(required=True)
    selling_price=fields.Float(readonly=True, copy=False)
    bedrooms=fields.Integer(default=2)
    living_area=fields.Integer()
    facades=fields.Integer()
    active = fields.Boolean(default=True)
    garage=fields.Boolean()
    garden=fields.Boolean()
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('or', 'Offer Recieved'), ('oa', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        required=True,
        copy=False,
        default='new'
    )
    garden_area=fields.Integer()
    garden_orientation=fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')]
    )
