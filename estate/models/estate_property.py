from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _sql_constraints = [
        ("nonnegative_property_expected_price", "CHECK(expected_price >= 0)", "The expected price of a property can't be negative."),
        ("nonnegative_property_selling_price", "CHECK(selling_price >= 0)", "The selling price of a property can't be negative."),
    ]
    _order = "id desc"

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesperson_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Property Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=fields.Datetime.add(fields.Datetime.today(), months=3), copy=False)
    expected_price = fields.Float(required=True)
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean(default=False)
    garden_area = fields.Integer(default=0)
    garden_orientation = fields.Selection(
        string="Garden orientation",
        selection=[
            ('north', 'North'),
            ('east', 'East'),
            ('south', 'South'),
            ('west', 'West'),
        ],
        default="north",
    )
    total_area = fields.Integer(compute="_compute_total_area")
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='State',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        required=True,
        copy=False,
        default="new",
    )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for estate in self:
            estate.total_area = estate.living_area + estate.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for estate in self:
            estate.best_price = max(estate.offer_ids.mapped("price") + [0])

    @api.onchange("garden")
    def _onchange_garden(self):
        for estate in self:
            if estate.garden:
                estate.garden_area = 10
                estate.garden_orientation = "north"
            else:
                estate.garden_area = 0
                estate.garden_orientation = ""

    def set_state_sold(self):
        for estate in self:
            if estate.state == "canceled":
                raise UserError("Canceled property can't be sold.")

            estate.state = "sold"
        return True

    def set_state_canceled(self):
        for estate in self:
            if estate.state == "sold":
                raise UserError("Sold property can't be canceled.")

            estate.state = "canceled"
        return True

    @api.constrains("selling_price", "expected_price")
    def _check_valid_selling_price(self):
        for estate in self:
            if (
                not float_is_zero(estate.selling_price, 1)
                and float_compare(estate.selling_price, 0.9 *
                estate.expected_price, 1) == -1
            ):
                raise ValidationError(_("The selling price must be at least 90% of the expected price."))

    @api.ondelete(at_uninstall=False)
    def prevent_delete_with_offer(self):
        for estate in self:
            if estate.state not in ("new", "canceled"):
                raise UserError(_("Can't delete a property that isn't new or canceled."))
