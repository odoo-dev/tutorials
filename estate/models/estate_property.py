from odoo import fields, models
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate properties"

    active = fields.Boolean(string="Active", default=True)
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('received', 'Offer Received'), ('accepted', 'Offer Accepted'), ('sold', 'Sold'), ('cancelled', 'Cancelled')],
        required=True,
        copy=False,
        default='new'
    )
    name = fields.Char(string="Name", required=True, default='Unknown')
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Availability", copy=False, default=fields.Date.today() + relativedelta(months=1))
    expected_price = fields.Float(string="Expected price", required=True)
    selling_price = fields.Float(string="Selling price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden area")
    garden_orientation = fields.Selection(
        string='Garden facing',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Garden facing")
    last_seen = fields.Date(string="Last seen", default=fields.Datetime.now)
