from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MyModel(models.Model):
    _name = "estate_property"
    _description = "Real Estate"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available From")
    expected_price = fields.Float(string="Expected Price")
    selling_price = fields.Float(string="Selling Price", default="0.00")
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string="Status",
        selection=[
            ("new", "New"),
            ("offer received", "Offer Received"),
            ("offer accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        default="new",
    )

    salesman_id = fields.Many2one(
        "res.users",  # The model this field relates to
        string="Salesman",  # Label for the field
        default=lambda self: self.env.user.partner_id,  # Set default to the current user
    )
    buyer_id = fields.Many2one(
        "res.partner",  # The model this field relates to
        string="Buyer",  # Label for the field
        copy=False,  # Prevent the field value from being copied when duplicating the record
    )
    property_type_id = fields.Many2one(
        "real.estate.property.type", string="Property Type"
    )
    tag_ids = fields.Many2many("real.estate.property.tag", string="tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Float(compute="_compute_total_area")
    best_offer = fields.Float(compute="_compute_best_offer")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price", "best_offer")
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max(record.offer_ids.mapped("price"))
            else:
                record.best_offer = 0.0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = False
            self.garden_orientation = False

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold property cannot be cancelled.")
            record.state = "cancelled"

    def action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled property cannot be sold.")
            record.state = "sold"

    @api.depends("offer_ids.price", "selling_price")
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max(record.offer_ids.mapped("price"))
            else:
                record.best_offer = 0.0

    _sql_constraints = [
        (
            "selling_price",
            "CHECK(selling_price >= 0)",
            "A property selling price must be strictly positive.",
        ),
        (
            "expected_price",
            "CHECK(expected_price >= 0)",
            "A property expected price must be strictly positive.",
        ),
    ]

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price > 0:
                price_per = (record.expected_price * 90) / 100
                if record.selling_price < price_per:
                    raise ValidationError(
                        "selling price cannot be lower than 90% of the expected price."
                    )
