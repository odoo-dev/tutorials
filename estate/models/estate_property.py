import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from odoo import api, fields, models


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate property model test description"
    _order = "id desc"

    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")
    name = fields.Char(required=True)
    description = fields.Text("Description of the Estate Propert Model")
    postcode = fields.Char("Post code")
    date_availability = fields.Date(
        "Availability date",
        default=lambda self: datetime.date.today() + datetime.timedelta(days=90),
        copy=False
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(copy=False, readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("west", "West"),
            ("east", "East")
        ]
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled")
        ],
        default="new",
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    salesperson_id = fields.Many2one("res.users", string="Salesperson")
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Property Offers")

    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'The expected price must be strictly positive.'
        )

    _check_selling_price = models.Constraint(
        'CHECK(selling_price >= 0)',
        'The selling price must be positive.'
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        self.total_area = self.garden_area + self.living_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for estate in self:
            estate.best_price = max(estate.offer_ids.mapped('price'), default=0)

    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price_percentage(self):
        for estate in self:
            if float_compare(
                estate.selling_price, (estate.expected_price * 0.9), 2
            ) < 0 and not float_is_zero(estate.selling_price, 2):
                raise ValidationError(self.env._("The selling price must be minimum 90% of the expected price"))

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_cancel(self):
        properties_to_cancel = self.filtered(lambda p: p.state != 'sold')
        if self - properties_to_cancel:
            raise UserError(self.env._("A sold property cannot be cancelled."))
        else:
            properties_to_cancel.state = 'cancelled'

    def action_mark_as_sold(self):
        properties_sold = self.filtered(lambda p: p.state != 'cancelled')
        if self - properties_sold:
            raise UserError(self.env._("A cancelled property cannot be sold."))
        else:
            properties_sold.state = 'sold'
