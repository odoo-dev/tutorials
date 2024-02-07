from odoo import models, fields

class estate_property(models.Model):
    _name = 'estate.property'
    _description = 'estate property table for real estate'

    name = fields.Char('name', default="Property name", required=True)
    description = fields.Text('description', default='some desc')
    postcode = fields.Char('postcode', default="ABCD")
    date_availability = fields.Date('date_availability')
    expected_price = fields.Float('expected_price', default=0.0, required=True)
    selling_price = fields.Float('selling_price', defaultcd=0.0)
    bedrooms = fields.Integer('bedrooms', default=0)
    living_area = fields.Integer('living_area', default=0)
    facades = fields.Integer('facades', default=0)
    garage = fields.Boolean('garage', default=False)
    garden = fields.Boolean('garden', default=False)
    garden_area = fields.Integer('garden_area', default=0)
    garden_orientation = fields.Selection([('n', 'North'),('s', 'South'),('w', 'West'),('e', 'East')])
