from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.exceptions import UserError,ValidationError
class EstateProperty(models.Model):
    _name ="estate.property"
    _description = "Estate property Model"
    _order="id desc"
    name= fields.Char(required=True) 
    description = fields.Char()
    postcode = fields.Char()
    date_availability = fields.Date(string='Available From',copy=False, default=lambda self: (date.today() + relativedelta(months=3)))
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly=True, copy= False)
    bedrooms = fields.Integer(default=2, copy=False)
    living_area = fields.Integer()  
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [('north', 'North'), 
         ('south', 'South'), 
         ('east', 'East'), 
         ('west', 'West')],
    )
    active=fields.Boolean(default=True)
    state=fields.Selection([('new','New'),
                            ('offer_received', 'OFFER RECEIVED'),
                            ('offer_accepted','OFFER ACCEPTED'),
                            ('sold','SOLD'),
                            ('cancelled','CANCELLED')],
                            default='new',
                            copy=False)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)                         
    partner_id=fields.Many2one('res.partner', copy=False,string='Buyer')

    #make relation with state.property.type
    property_type_id=fields.Many2one('estate.property.type',string='Property Types')
    #make relation with state.property.tag
    tag_ids=fields.Many2many( "estate.property.tag")
    #make relation with state.property.offer
    offer_ids=fields.One2many('estate.property.offer','property_id')

    #new compute fields 
    total_area=fields.Integer(compute=("_compute_total_area"))
    best_price=fields.Float(compute=("_compute_best_offer"))

    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area=record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            record.best_price=max(record.offer_ids.mapped('price'), default=0)

    @api.onchange("garden")
    def _onchange_expected_price_set_value(self):
            if self.garden:
                self.garden_area=10
                self.garden_orientation="north"
            else:
               self.garden_area=0 
               self.garden_orientation = None          
    # action for the sold button 
    def action_do_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError("Cancelled properties can not be sold.")    
            else:
                record.state="sold"
        return True              
     # action for the cancel button 
    def action_do_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError("Sold properties can not be cancelled")
            else:    
                record.state="cancelled"
        return True    
    
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)',
         'The Expected price must be Positive a value.')
    ]
    #constraints for the selling_price_price field
    _sql_constraints=[
        ('check_selling_price','CHECK(selling_price >= 0)',
        'The Selling price must be a Positive value'),
    ]
    #Python constraints on the selling_price field
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < (90*record.expected_price)/100:
                raise ValidationError("The sellig price can not be Lower than the 90 Percentage of Expected price")

    @api.ondelete(at_uninstall=False)
    def unlink_expect_state_is_not_new_or_cancelled(self):
        for record in self:
            # Check if the state is not 'New' or 'Cancelled'
            if record.state not in ['new', 'cancelled']:
                raise UserError("Only New or Cancelled properties can be deleted")
            else:    
                return super(EstateProperty, self).unlink_expect_state_is_not_new_or_cancelled()




    




