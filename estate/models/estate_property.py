from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(required=True, default="Unknown")
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    description = fields.Text()
    tag_ids = fields.Many2many("estate.property.tags", string="Tags")
    salesman_id = fields.Many2one("res.users", default=lambda self: self.env.user.id)
    buyer_id = fields.Many2one(
        "res.partner", default=lambda self: self.env.user.id, copy=False
    )
    postcode = fields.Char()
    date_availability = fields.Date(copy=False)
    expected_price = fields.Float(required=True, default=15.6, tracking=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
        string="Garden Orientation",
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        copy=False,
        default="new",
        tracking=True,
    )
    offer_ids = fields.One2many(
        "estate.property.offers", "property_id", string="Offers"
    )
    _check_expected_price = models.Constraint(
        "CHECK(expected_price > 0)", "Expected price must be positive."
    )
    _check_selling_price = models.Constraint(
        "CHECK(selling_price > 0)", "Property selling price must be positive."
    )

    @api.constrains("expected_price", "selling_price")
    def _check_selling_price(self):
        if not float_is_zero(self.selling_price, 2):
            if float_compare(self.selling_price, (self.expected_price * 0.9), 2) == -1:
                raise ValidationError(
                    "Selling Price must not be less than 90% of expected price."
                )

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for realEstateProperty in self:
            realEstateProperty.total_area = (
                    realEstateProperty.living_area + realEstateProperty.garden_area
            )

    # @api.onchange("living_area", "garden_area")
    # def _compute_total_area(self):
    #     for record in self:
    #         record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for property in self:
            # valid = property.offer_ids.filtered(lambda offer: offer.status != "refused")
            # property.best_price = max(valid.mapped("price"), default=0) if valid else 0
            property.best_price = max(property.offer_ids.mapped("price")) if property.offer_ids else 0

    # @api.depends("offer_ids")
    # def _compute_best_price(self):
    # if self.offer_ids:
    #     price_list=[]
    #         price_list.append(offer.price)
    #     for i in range(len(price_list)):
    #         for j in range(len(price_list)):
    #             if price_list[i]>=price_list[j]:
    #                 self.best_price= price_list[i]
    # else:
    #     self.best_price=0
    # self.best_price = 0
    # if self.offer_ids:
    #     for offer in self.offer_ids:
    #         if offer.price > self.best_price:
    #             self.best_price = offer.price

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    def set_sold(self):
        if self.state == "new":
            raise UserError("Create a offer to accept and sell the property")
        elif self.state == "cancelled":
            raise UserError("Cancelled Properties Cannot be Sold")
        elif self.state == "offer_accepted":
            self.state = "sold"
        else:
            raise UserError("Please accept offer to sell a property")

        return True

    def set_cancel(self):
        if self.state == "sold":
            raise UserError("Sold Properties cannot be Cancelled")
        else:
            self.state = "cancelled"

        self.offer_ids.status = "refused"
        return True

    @api.ondelete(at_uninstall=True)
    def _unlink_if_new_or_cancelled(self):
        for property in self:
            if property.state not in ["cancelled", "new"]:
                raise UserError("Only new and cancelled properties can be deleted.")
