from odoo import fields, models, api
from odoo.api import ondelete
from datetime import date, datetime,timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Model for Real Estate Properties"
    _order = "id desc"

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
    garden = fields.Boolean(string="Garden ?")
    garden_area = fields.Integer(string = "Garden Area (in sqm)")
    garden_orientation = fields.Selection([('north','North'),('south','South'),('east','East'),('west','West')] , string="Garden Orientation")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    sales_person_id = fields.Many2one("res.users", string="Salesman", default=lambda self:self.env.user)
    tag_ids = fields.Many2many("estate.property.tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Integer(string="Total Area(in sqm)", compute="_compute_total_area")
    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")
    property_image = fields.Image(string="Image")
    company_id = fields.Char(default=(lambda self : self.env.user.company_id))

    active = fields.Boolean(default=True)
    state = fields.Selection([('new', 'New'),('offer_received', 'Offer Received'),('offer_accepted', 'Offer Accepted'),('sold', 'Sold'),('canceled', 'Canceled')], string='Status', default='new', copy=False, required=True)

    #SQL constraints
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "The expected price must be strictly positive"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The selling price must be positive"),
    ]

    #python constraints
    @api.constrains("expected_price", "selling_price")
    def _check_price_difference(self):
        for record in self:
            if (
                not float_is_zero(record.selling_price, precision_rounding=0.01)
                and float_compare(record.selling_price, record.expected_price * 90.0 / 100.0, precision_rounding=0.01) < 0
            ):
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! "
                    + "You must reduce the expected price if you want to accept this offer."
                )

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
    
    #crud methods
    @ondelete(at_uninstall = True)
    def _check_delete_property_condition(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("Properties with state other than 'New' or 'Canceled' cannot be deleted.")

    #buttons
    def cancel_state(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold Properties can not be canceled")
            else:
                record.state = 'canceled'
    
    def sold_state(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("Canceled Properties can not be sold")
            else:
                record.state = 'sold'
