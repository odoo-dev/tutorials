from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.orm.utils import ValidationError
from odoo.tools import date_utils, float_compare


class EstateProperty(models.Model):
    _name: str = "estate.property"
    _active = True
    _description: str | None = None
    _order = "id desc"

    name = fields.Char()
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date('Availability Date', copy=False, default=lambda self: date_utils.add(fields.Date.today(), months=3))
    expected_price = fields.Float()
    selling_price = fields.Float(readonly=True, copy=False)
    bedroom = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garage = fields.Boolean()
    garden_orientation = fields.Selection(
        selection=[("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")],
        string='Type',
        help="Type is used to separate Leads and Opportunities")
    state = fields.Selection(
        [("new", "New"), ("received", "Offer Received"), ("accepted", "Offer Accepted"), ("sold", "Sold"), ("cancelled","Cancelled")],
        copy=False,
        default="new")
    property_type_id = fields.Many2one("estate.property.type")
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.uid)
    buyer_id = fields.Many2one("res.partner", copy=False)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id")
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_price')

    _check_expected_price = models.Constraint(
        'CHECK(expected_price > 0)',
        'Prices must be positive',
    )

    @api.depends('garden_area', 'living_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max([0, *record.offer_ids.mapped('price')])


    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if float_compare(record.selling_price, record.expected_price * 0.9, 2) < 0:
                raise ValidationError("Can not accept offer if offered price is lower than 90% of expected")

    @api.ondelete(at_uninstall=False)
    def _unlink_if_user_inactive(self):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError(_("Can't delete a property wich is neither new nor cancelled!"))

    def _check_state_compatibility_because(self, record, state, message):
        if record.state == state:
            raise UserError(message)

    def sell(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError(_("Canceled property can not be sold"))
            record.state = "sold"
        return True

    def cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError(_("Sold property can not be canceld"))
            record.state = "cancelled"
        return True
