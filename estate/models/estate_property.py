from odoo import fields, models
from datetime import date, datetime,timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Model for Real Estate Properties"
    active = fields.Boolean(default=True)

    name = fields.Char(string = "Name" , required=True, default="Unknown")
    description = fields.Text(string = "Description")
    postcode = fields.Char(string = "Post Code")
    date_availability = fields.Date(string="Date of Availability", copy=False, default=(date.today() + timedelta(days=90)).strftime("%Y-%m-%d"))
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string = "Bedrooms", default="2")
    living_area = fields.Integer(string = "Living Area (in square meters)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage ?")
    garden = fields.Boolean(string="Garden ?")
    garden_area = fields.Integer(string = "Garden Area (in square meters)")
    garden_orientation = fields.Selection([('north','North'),('south','South'),('east','East'),('west','West')] , string="Garden Orientation")
    
    state = fields.Selection([('new', 'New'),('offer_received', 'Offer received'),('offer_accepted', 'Offer Accepted'),('sold', 'Sold'),('cancelled', 'Cancelled')], string='Status', default='new', copy=False, required=True)