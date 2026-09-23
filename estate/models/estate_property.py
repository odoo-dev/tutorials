from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "This is the model for the real estate"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Datetime.add(fields.Datetime.today(), months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(string='Orientation',
    selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], help="Garden Orientation (North, South, East, West)")
    active = fields.Boolean(default=True)
    stage = fields.Selection(string="Stage",
    selection=[("new", "New"), ("offer received", "Offer Received"), ("offer accepted", "Offer Accepted"), ("sold", "Sold"), ("cancelled", "Cancelled")],
    required=True, default="new", copy=False)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    salesperson_id = fields.Many2one("res.users", string="SalesPerson")
    property_tags_ids = fields.Many2many("estate.property.tag", string="Property Tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Float(compute="_compute_total")
    best_price = fields.Float(compute="_compute_best_offer")
    _order = "id desc"

    @api.depends("garden_area", "living_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids")
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = "north"
            else:
                record.garden_area = None
                record.garden_orientation = None

    def sell_property(self):
        for record in self:
            if record.stage != 'cancelled':
                record.stage = 'sold'
                return True
            UserError(self.env._("Unable to sell cancelled property"))
            return False

    def cancel_property(self):
        for record in self:
            if record.stage != 'sold':
                record.stage = 'cancelled'
                return True
            UserError(self.env._("Unable to cancel sold property"))
            return False

    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'Expected price must be strictly positive'
    )

    _check_selling_price = models.Constraint(
        'CHECK (selling_price > 0)',
        'Selling price must be strictly positive'
    )

    @api.constrains('selling_price', 'expected_price')
    def _check_good_pricing(self):
        for record in self:
            if not float_is_zero(record.selling_price, 2) and float_compare(record.selling_price, record.expected_price * 0.9, 2) < 0:
                raise ValidationError("The selling price must be at least 90% of the expected price")
