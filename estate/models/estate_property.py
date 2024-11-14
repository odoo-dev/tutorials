from odoo import fields, models
from dateutil.relativedelta import relativedelta
from datetime import date
class EstateProperty(models.Model):
    _name ="estate.property"
    _description = "Estate property Model"
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
         ('east', 'Easestate_propertyt'), 
         ('west', 'West')],
    )
    active=fields.Boolean(default=True)
    state=fields.Selection([('new','New'),
                            ('offer recieved', 'Offer Received'),
                            ('offer accept','Offer Accept'),
                            ('sold','Sold'),
                            ('cancelled','Cancelled')],
                            default='new',
                            copy=False)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True, default=lambda self: self.env.user)                         
    partner_id=fields.Many2one('res.partner', copy=False,string='Buyer')

    #make relation with state.property.type
    property_type_id=fields.Many2one('estate.property.type',string='Property Types')
    #make relation with state.property.tag
    tag_ids=fields.Many2many("estate.property.tag")
    #make relation with state.property.offer
    offer_ids=fields.One2many('estate.property.offer','property_id')