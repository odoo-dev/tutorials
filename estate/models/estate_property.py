from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero

from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From",
        copy=False,
        default=lambda self: fields.Date.to_string(
            fields.Date.from_string(fields.Date.context_today(self))
            + relativedelta(months=3)
        ),
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        help="Garden Orientation",
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesperson_id = fields.Many2one(
        "res.users", string="Salesman", default=lambda self: self.env.user
    )
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
    offer_ids = fields.One2many(
        "estate.property.offer", "property_id", string="Property Offers"
    )
    total_area = fields.Integer(
        "Total Area (sqm)", compute="_compute_total_area", readonly=True
    )
    best_price = fields.Float(
        "Best Price", compute="_compute_best_price", readonly=True
    )
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("cancelled", "Cancelled"),
            ("sold", "Sold"),
        ],
        string="Status",
        default="new",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0.0)",
            "The expected price must be positive.",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price > 0.0)",
            "The selling price must be positive.",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.mapped("offer_ids.price"))
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "south"
        else:
            self.garden_area = None
            self.garden_orientation = None

    def action_sold(self):
        if self.state != "cancelled":
            self.state = "sold"
            return True
        else:
            raise UserError("The property cannot be sold once it is cancelled")

    def action_cancel(self):
        if self.state != "sold":
            self.state = "cancelled"
            return True
        else:
            raise UserError("The property cannot be cancelled once it is sold")

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if not (
                not float_is_zero(record.selling_price, precision_digits=3)
                and float_compare(
                    record.selling_price,
                    record.expected_price * 0.9,
                    precision_digits=3,
                )
                >= 1
            ):
                raise ValidationError(
                    "The selling price cannot be lower than 90% of the expected price."
                )

    @api.ondelete(at_uninstall=False)
    def _ondelete_property(self):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError(
                    "You cannot delete a property that is not new or cancelled."
                )
