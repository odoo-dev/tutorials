from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _sql_constraints = [('expected_price_positive', 'CHECK(expected_price > 0)', 'Expected price must be positive!'),
                        ('selling_price_positive', 'CHECK(selling_price > 0)', 'Selling price must be positive!')]
    _order = 'id desc'

    name = fields.Char(string='Property Name', required=True)
    description = fields.Text(string='Description')
    postcode = fields.Char(string='Postcode')
    date_availability = fields.Date(string='Availability Date', copy=False,
                                    default=fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='Bedrooms', default=2)
    living_area = fields.Float(string='Living Area (sqm)')
    facades = fields.Integer(string='Facades', default=1)
    garage = fields.Boolean(string='Garage', default=False)
    garden = fields.Boolean(string='Garden', default=False)
    garden_area = fields.Float(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        string='Garden Orientation', default='north')
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection(
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('cancelled', 'Cancelled')], string='State', default='new')
    property_type_id = fields.Many2one(comodel_name='estate.property.type', string='Property Type')
    partner_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    user_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    tag_ids = fields.Many2many(comodel_name='estate.property.tag', string='Tags')
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_id', string='Offers')
    total_area = fields.Float(string='Total Area (sqm)', compute='_compute_total_area', readonly=True)
    best_price = fields.Float(string='Best Offer Price', compute='_compute_best_price', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area if record.living_area and record.garden_area else 0.0

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_sold(self):
        for record in self:
            if record.state != 'cancelled':
                if record.offer_ids and record.state == 'offer_accepted':
                    record.selling_price = record.best_price
                    record.state = 'sold'
                elif record.state == 'new' or record.state == 'offer_received':
                    raise ValidationError("You must accept an offer before marking the property as sold.")
            else:
                raise ValidationError("You cannot mark a cancelled property as sold.")

    def action_cancel(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'cancelled'

    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.offer_ids and record.state == 'offer_accepted' and float_compare(record.selling_price,
                                                                                       0.9 * record.expected_price,
                                                                                       precision_digits=2) < 0:
                raise ValidationError("Selling price cannot be lower than 90% of the expected price.")

    @api.ondelete(at_uninstall=True)
    def _unlink_property(self):
        for record in self:
            if record.state not in ['new', 'cancelled']:
                raise ValidationError("You cannot delete a property that is not new or cancelled.")
