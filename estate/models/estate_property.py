from odoo import fields, models, api
from datetime import date, datetime,timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Model for Real Estate Properties"

    name = fields.Char(string = "Name" , required=True, default="Unknown")
    description = fields.Text(string = "Description")
    postcode = fields.Char(string = "Post Code")
    date_availability = fields.Date(string="Date of Availability", copy=False, default=(date.today() + timedelta(days=90)).strftime("%Y-%m-%d"))
    last_seen = fields.Datetime("Last Seen", default=fields.Datetime.now)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string = "Bedrooms", default="2")
    living_area = fields.Integer(string = "Living Area (in sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage ?")
    garden = fields.Boolean(string="Garden ?", )
    garden_area = fields.Integer(string = "Garden Area (in sqm)")
    garden_orientation = fields.Selection([('north','North'),('south','South'),('east','East'),('west','West')] , string="Garden Orientation")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    sales_person_id = fields.Many2one("res.users", string="Salesman", default=lambda self:self.env.user)
    tag_ids = fields.Many2many("estate.property.tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Integer(string="Total Area(in sqm)", compute="_compute_total_area")
    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")

    active = fields.Boolean(default=True)
    state = fields.Selection([('new', 'New'),('offer_received', 'Offer received'),('offer_accepted', 'Offer Accepted'),('sold', 'Sold'),('cancelled', 'Cancelled')], string='Status', default='new', copy=False, required=True)


    #computed methods
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends("offer_ids")
    def _compute_best_offer(self):
        for record in self:
            best_offer = max(record.offer_ids.mapped("price"), default=0.0)
            record.best_offer = best_offer
    
    #onchange method
    @api.onchange("garden")
    def _onchange_garden(self):
            if self.garden:
                self.garden_area = 10 
                self.garden_orientation = 'north'
            else:
                self.garden_area = 0
                self.garden_orientation = False
