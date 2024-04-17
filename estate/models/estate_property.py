from odoo import models,fields

class Property(models.Model):

    _name = "estate_property"
    _description = "The properties of the real estate property"
    name = fields.Char(required = True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy = False, default = fields.Date.add(fields.Date.today(), months = 3))
    expected_price = fields.Float(required = True)
    selling_price = fields.Float(readonly = True, copy = False)
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        selection = [
            ('North', 'North'), 
            ('South', 'South'), 
            ('East', 'East'), 
            ('West', 'West'),
        ],
    )
    active = fields.Boolean(default = True)
    state = fields.Selection(
        selection = [
            ('New', 'New'), 
            ('Offer Received', 'Offer Received'), 
            ('Offer Accepted', 'Offer Accepted'), 
            ('Sold', 'Sold'), 
            ('Canceled', 'Canceled')
        ],
        required = True,
        copy = False,
        default = 'New',
    )
    property_type_id = fields.Many2one("estate_property_type", string = "Property Type")
    user_id = fields.Many2one('res.users', string="Salesperson", default=lambda self : self.env.user)
    partner_id = fields.Many2one('res.partner', string="Buyer", copy = False)
    property_tag_ids = fields.Many2many('estate_property_tag')
    property_offer_ids = fields.One2many('estate_property_offer', 'property_id', string = 'Offers')
    
