from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = """
    
    This is a description as requested in the tutorial to get rid of the following warning:

    2025-06-30 09:12:55,798 44228 WARNING rd-demo-enterprise odoo.models: The model estate.property has no _description 
    """
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)', 'The expected price must be strictly positive.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be strictly positive.')
    ]
    _order = "id desc"

    name = fields.Char(required=True)

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", copy=False)
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user)

    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date("Available From", copy=False, default=fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    best_offer = fields.Float(readonly=True, compute="_compute_max")
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ]
    )
    total_area = fields.Integer("Total Area (sqm)", compute="_compute_total_area")
    state = fields.Selection(
        selection = [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        default='new',
        copy=False,
        required=True,
    )
    active = fields.Boolean(default=True)

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
         
    @api.depends("offer_ids")
    def _compute_max(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped('price'), default=0)

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    @api.constrains('expected_price', 'selling_price')
    def _check_minimum_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_digits=2) and \
                float_compare(
                    record.selling_price,
                    0.9 * record.expected_price,
                    precision_digits=2) == -1:

                raise ValidationError(f'The selling price must be at least 90% of the expected price! You must reduce the expected price if you want to accept this offer.')
    
    @api.ondelete(at_uninstall=False)
    def _unlink_forbidden_except_new_or_cancel(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError(_("Deletion is only allowed in the New and Cancelled stages."))
            
    def mark_as_sold(self):
        if self.state != 'cancelled':
            if any(offer.status == 'accepted' for offer in self.offer_ids):
                self.state = 'sold'
            else:
                raise UserError(_("There is no accepted offer for this property."))
        else:
            raise UserError(_("Cancelled property cannot be sold."))
        return True
    def mark_as_cancelled(self):
        if self.state != 'sold':
            self.state = 'cancelled'
        else:
            raise UserError(_("Sold property cannot be cancelled"))
        return True