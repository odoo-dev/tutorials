from odoo import api, fields, models
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
         ('east', 'East'), 
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
    def _onchange_set_value(self):
            if self.garden:
                self.garden_area=10
                self.garden_orientation="north"
            else:
               self.garden_area=0 
               self.garden_orientation = None    

                


