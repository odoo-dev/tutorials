from odoo import api,models, fields
from odoo.exceptions import UserError,ValidationError
from odoo.tools.float_utils import  float_compare,float_is_zero

class EstateProperty(models.Model):
    _name ="estate.property"
    _description = "Estate property Model"
    _order="id desc"
    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', "The expected price must be strictly positive."),
        ('selling_price_positive', 'CHECK(selling_price >= 0)', "The selling price must be positive."),
    ]  
    name= fields.Char(required=True) 
    description = fields.Char()
    active=fields.Boolean(default=True)
    postcode = fields.Char()
    date_availability = fields.Date("Available From", copy=False, default=fields.Date.add(fields.Date.today(), months=3))
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly=True, copy= False)
    bedrooms = fields.Integer(default=2, copy=False)
    living_area = fields.Integer()  
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=
        [('north', 'North'), 
        ('south', 'South'), 
        ('east', 'East'), 
        ('west', 'West')],
        default='north', required=True
    )
    state = fields.Selection(string="Status",selection=[
        ('new','New'),
        ('offer received','Offer Received'),
        ('offer accepted','Offer Accepted'),
        ('sold','Sold'),
        ('cancelled','Cancelled'),
    ], default='new', required=True)
    property_type_id = fields.Many2one("estate.property.type")
    salesman = fields.Many2one("res.users",  default=lambda self: self.env.user)
    buyer = fields.Many2one("res.partner")
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_id',
        string='Offers')
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price") 
        
    @api.ondelete(at_uninstall=False)
    def _unlink_if_inappropriate_state(self):
        for record in self:
            if record.state not in ['new','cancelled']:
                raise UserError("Only New and Cancelled Properties can be deleted")
        return True
    
    @api.depends("garden_area","living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area
            
    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped('price')
            if prices:
                record.best_price = max(prices)
            else:
                record.best_price = 0.0  
        return True
    
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = None
            self.garden_orientation = None
            
    @api.constrains('expected_price', 'selling_price')
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price, precision_rounding=0.01): 
                if float_compare(record.selling_price, record.expected_price * 0.9, precision_rounding=0.01) < 0:
                    raise ValidationError("The selling price cannot be lower than 90 percent of the expected price.")
            
    def action_sell_property(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError('Cancelled Properties cannot be Sold')
            else:
                record.state = 'sold'
        return True
    
    def action_cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Sold Properties cannot be Cancelled')
            else:
                record.state = 'cancelled'
        return True
            