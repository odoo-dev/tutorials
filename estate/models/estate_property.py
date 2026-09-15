from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    # Private attributes
    _name = "estate.property"
    _description = "This is estate property model"
    _order = "id desc"

    # Field declarations
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=lambda self: fields.Date.add(fields.Date.today(), months=3)
    )
    expected_price = fields.Float(required=True)
    best_price = fields.Float(compute="_find_best_price")
    selling_price = fields.Float(readonly=True, copy=False)
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
            ("east", "East"),
            ("west", "West"),
        ],
    )
    state = fields.Selection(
        required=True,
        copy=False,
        default="new",
        selection=[
            ("new", "New"),
            ("offer_recieved", "Offer Recieved"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
    )
    active = fields.Boolean(default=True)
    total_area = fields.Integer(compute="_compute_total_area")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    line_ids = fields.One2many("estate.property.list", "model_id")

    # SQL constraints and indexes
    _expected_price_constraint = models.Constraint(
        "CHECK (expected_price >= 0)", "Expected Price must be positive or zero."
    )
    _selling_price_constraint = models.Constraint(
        "CHECK (selling_price >= 0)", "Selling Price must be positive."
    )

    # Compute, inverse and search methods
    @api.depends("salesperson_id")
    def _find_best_price(self):
        for property in self:
            property.best_price = max(property.offer_ids.mapped("price"), default=0)

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for property in self:
            property.total_area = property.living_area + property.garden_area

    # Constrains methods and onchange methods
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    @api.ondelete(at_uninstall=False)
    def _unlink_if_estate_new_or_cancelled(self):
        if any(estate.state not in ["new", "cancelled"] for estate in self):
            raise UserError(
                "Can't delete an estate, only New or Cancelled estates can be deleted!"
            )

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.state == "sold" and (
                float_compare((record.expected_price * 0.90), record.selling_price, 2)
                != -1
            ):
                raise UserError(
                    _("Selling price cannot be lower than 90% /of the expected price.")
                )

    # CRUD methods

    # Action methods
    def action_sold_property(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("Cancelled property cannot be sold"))
            else:
                record.state = "sold"

    def action_cancel_property(self):
        for record in self:
            if record.state == "sold":
                raise UserError(_("Sold property cannot be cancelled"))
            else:
                record.state = "cancelled"

    # Business methods
    def action_sell_to_offer(self, offer_buyer_id, offer_selling_price):
        for record in self:
            record.buyer_id = offer_buyer_id
            record.state = "sold"
            record.selling_price = offer_selling_price
        return True

    def action_change_state(self, newState):
        for estate in self:
            estate.state = newState


class EstatePropertyList(models.Model):
    # Private attributes
    _name = "estate.property.list"
    _description = "This is estate property model list"

    # Field declarations
    model_id = fields.Many2one("estate.property")
    name = fields.Char(required=True)
    expected_price = fields.Float(required=True)
    state = fields.Selection(
        required=True,
        copy=False,
        default="new",
        selection=[
            ("new", "New"),
            ("offer_recieved", "Offer Recieved"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
    )
