from dateutil.relativedelta import relativedelta

from odoo import models, fields
from odoo.odoo.api import readonly


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Properties'
    _order='create_date desc'

    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_available = fields.Date("Date Available", copy=False, default=fields.Date.today() + relativedelta(days=90))
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')]
    )
    active = fields.Boolean("Active", default=True)
    state = fields.Selection(
        string="State",
        selection=[("new", "New"),
                   ("offer_received", "Offer Received"),
                   ("offer_accepted", "Offer Accepted"),
                   ("sold", "Sold"),
                   ("cancelled", "Cancelled")],
        copy=False,
        required=True,
        default="new"
    )
    partner_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    user_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.uid)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    tag_ids=fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")