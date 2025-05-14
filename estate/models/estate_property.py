from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
from dateutil.relativedelta import relativedelta


class EstatePropertyModel(models.Model):
    _name = "estate_property"
    _description = "Real estate properties"
    _order = "id desc"
    
    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price > 0)", "A property expected price must be strictly positive"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "A property selling price must be positive"),
    ]

    name = fields.Char("Title", required=True)
    property_type_id = fields.Many2one("estate_property_type", string="Property Type")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        copy=False, default=fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
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
        required=True,
        copy=False,
        default='new',
    )

    buyer_id = fields.Many2one("res.partner", copy=False)
    salesperson_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate_property_tag")
    offer_ids = fields.One2many("estate_property_offer", "property_id", string="Offers")

    total_area = fields.Integer(compute="_compute_area")
    best_price = fields.Float(compute="_compute_best_price")
    
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    
    @api.depends("living_area", "garden_area")
    def _compute_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = min(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0           

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_set_property_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled properties cannot be sold")
            
            record.state = "sold"

        return True
    
    def action_set_property_cancelled(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties cannot be cancelled")
            
            record.state = "cancelled"

        return True
    
    @api.constrains("selling_price", "expected_price")
    def _checking_selling_price(self):
        print("fuction called")
        for record in self:
            if not float_utils.float_is_zero(record.selling_price, precision_digits=2) and \
                float_utils.float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError("Selling price cannot be lower than 90% of the expected price")
            
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_and_cancelled(self):
        if any(record.state != "new" and record.state != "cancelled" for record in self):
            raise UserError("Deletion of a property of state other than ‘New’ or ‘Cancelled’ is prohibitied")
