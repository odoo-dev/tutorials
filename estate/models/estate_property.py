from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare


class estateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property Model"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, string="Name", tracking=True)
    description = fields.Text(tracking=True)
    postcode = fields.Char()
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    image = fields.Binary()
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type", string="Property Type"
    )
    date_availability = fields.Date(
        copy=False,
        default=fields.Date.today() + relativedelta(months=3),
        string="Available From",
        tracking=True,
    )
    expected_price = fields.Float(required=True, tracking=True)
    selling_price = fields.Float(readonly=True, copy=False, tracking=True)
    bedrooms = fields.Integer(default=2, tracking=True)
    living_area = fields.Integer(string="Living Area (sqm)", tracking=True)
    facades = fields.Integer(tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    garage = fields.Boolean(tracking=True)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False, tracking=True)
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        tracking=True,
        default=lambda self: self.env.user,
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string=" ")
    state = fields.Selection(
        string="State",
        selection=[
            ("new", "New"),
            ("offer_recieved", "Offer Recieved"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
        tracking=True,
    )
    garden = fields.Boolean(tracking=True)
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        tracking=True,
    )
    total_area = fields.Integer(
        compute="_compute_total_area", string="Total Area (sqm)"
    )
    best_price = fields.Float(compute="_compute_best_price", string="Best Price")

    # constraints
    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price>=0)",
            "The expected price is always positive number",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price>=0)",
            "The selling price is always positive number",
        ),
    ]

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        self.best_price = max(self.offer_ids.mapped("price"), default=0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 20
            self.garden_orientation = "north"
        else:
            self.garden_area = None
            self.garden_orientation = None

    def action_cancel(self):
        for record in self:
            if not record.state == "sold":
                record.state = "canceled"
                return True
        raise UserError(("You can not cancel a sold property."))

    def action_sold(self):
        for record in self:
            if not record.state == "canceled":
                record.state = "sold"
                return True
        raise UserError(("You can not sell a cancelled property."))

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, 1e-9):
                if float_compare(record.selling_price, 0.9 * (record.expected_price), 2) == (-1):
                    raise ValidationError(
                        "The selling price cannot be lower than 90 percent of the expected price. You must reduce the expected price in order to accept that offer"
                    )

    @api.ondelete(at_uninstall=False)
    def _unlink_if_property_canceled_new(self):
        for property in self:
            if not (property.state == "new" or property.state == "canceled"):
                raise UserError("Can only delete a new or cancelled property!")
