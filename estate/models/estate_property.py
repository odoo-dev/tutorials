from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Property data model"
    _order = "id desc"
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
        'The expected price of a property MUST be postive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
        'The selling price of a property MUST be postive.'),
    ]

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda _self: fields.Date.add(fields.Date.today(), months=3), copy=False)
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
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='new',
        copy=False
    )

    # Relations
    property_type_id = fields.Many2one(comodel_name="estate.property.type")
    property_tag_ids = fields.Many2many(comodel_name='estate.property.tag')
    property_offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id')
    user_id = fields.Many2one(comodel_name='res.users', string='Salesperson', default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Buyer', copy=False)

    # computed
    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    # region Compute methodes
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('property_offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.property_offer_ids.mapped('price'), default=0)

    # endregion

    # region onchange
    @api.onchange('garden')
    def _onchange_garden(self):
        self.garden_area = 10 if self.garden else False
        self.garden_orientation = 'north' if self.garden else False

    # endregion

    # region Constraint
    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=3):
                continue

            if float_compare(value1=record.selling_price, value2=(0.9 * record.expected_price), precision_digits=3) == -1:
                raise ValidationError(self.env._("Selling price must be at least 90% of the expected price!"))

    # endregion

    # region CRUD
    @api.ondelete(at_uninstall=True)
    def prevent_delete(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError(self.env._("you Cann't delete a property that is not new or cancelled!"))

    # endregion

    # region actions
    def action_set_cancelled(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(self.env._("Sold properties can not be cancelled!"))
            record.state = 'cancelled'

    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError(self.env._("Cancelled properties can not be sold!"))
            record.state = 'sold'

    def action_set_offer_accepted(self, offer):
        if self.state == 'offer_accepted':
            raise UserError(self.env._("this property has already an accepted offer!!"))
        self.state = 'offer_accepted'
        self.selling_price = offer.price
        self.partner_id = offer.partner_id

    def action_set_offer_received(self):
        self.state = 'offer_received'

    # endregion
