# 19.0-tutorials-frtan

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate properties'
    _order = 'id desc'
    # _sql_constraints = [
    #     ('expected_price_positive', 'check (expected_price > 0)', 'The expected price must be strictly positive'),
    #     ('selling_price_positive', 'check (selling_price >= 0)', 'The selling price must be positive'),
    # ]
    _expected_price_positive = models.Constraint(
        'check (expected_price > 0)', # PostgreSQL language
        'The expected price must be strictly positive'
    )
    _selling_price_positive = models.Constraint(
        'check (selling_price >= 0)',
        'The selling price must be positive'
    )

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        default=fields.Date.add(fields.Date.today(), months=3),
        string='Available From',
        copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ])
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string='Status',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='new'
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type", group_expand='_read_group_property_type_ids')
    salesperson_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", copy=False, string="Buyer")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area (sqm)")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    @api.model
    def _read_group_property_type_ids(self, stages, domain):
        property_type_ids = stages._search([], bypass_access=True)
        return stages.browse(property_type_ids)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped('price')
            record.best_price = max(prices) if prices else 0
            # record.best_price = max(o.price for o in record.offer_ids)

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    # This method will be called in estate.property.offer model
    def change_state_when_offer_received(self, offered_price: float):
        # solution 2, create the error in the estate.property model
        prices = self.offer_ids.mapped('price')
        print(offered_price)
        if prices and offered_price < max(prices):
                raise UserError(f"The offer must be higher than {max(prices)}")
        self.state = 'offer_received'

    @api.constrains('selling_price')
    def _check_selling_price(self):
        if self.selling_price:
            if self.selling_price < (self.expected_price * 0.9):
                raise ValidationError("The selling price must be at least 90% of the expected price. You must reduce the price!")

    @api.ondelete(at_uninstall=False)
    def _unlink_property(self):
        if any(record.state != 'new' or record.state != 'cancelled' for record in self):
            raise UserError("Property cannot be deleted unless its stage is 'New' or 'Cancelled'")

    def action_cancel_estate_property(self):
        if self.state == 'sold':
            raise UserError("Sold properties cannot be cancelled.")
        else:
            self.state = 'cancelled'

    def action_sold_estate_property(self):
        if self.state == 'cancelled':
            raise UserError("Cancelled properties cannot be sold.")
        else:
            self.state = 'sold'