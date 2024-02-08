from odoo import fields, models
from dateutil.relativedelta import relativedelta

class estateProperty(models.Model):
    _name = "estate.property"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Estate Property Model"

    name = fields.Char(required=True, string='Name', tracking=True)
    description = fields.Text(tracking=True)
    postcode= fields.Char()
    date_availability=fields.Date(copy=False, default=fields.Date.today()+relativedelta(months=3), string='Available From', tracking=True)
    expected_price=fields.Float(required=True,tracking=True)
    selling_price=fields.Float(readonly=True, copy=False,tracking=True)
    bedrooms=fields.Integer(default=2, tracking=True)
    living_area=fields.Integer(string='Living Area (sqm)', tracking=True)
    facades=fields.Integer(tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    garage=fields.Boolean(tracking=True)
    garden=fields.Boolean(tracking=True)
    state = fields.Selection(
        string='State',
        selection=[('new', 'New'), ('or', 'Offer Recieved'), ('oa', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        required=True,
        copy=False,
        default='new',
        tracking=True
    )
    garden_area=fields.Integer()
    garden_orientation=fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        tracking=True
    )
