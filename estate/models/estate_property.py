from odoo import fields, models

class Property(models.Model):
    _name = 'estate.property'
    _description = 'Real estate property'
    
    name = fields.Char('Property Name', required=True, translate=True)
    description = fields.Text('Property Description', required=False, translate=True)
    postcode = fields.Char('Postcode', required=True)
    property_type = fields.Selection('Property Type', [('appartment', 'Appartment'), ('house', 'House')], required=True, default='accounts')
    date_availability = fields.Date('Available From', default=fields.Date.today())
    expected_price = fields.Float('Expected Price', 2,)
    best_offer = fields.Float('Best Offer', 2, default=0.0)
    selling_price = fields.Float('Selling Price', 2, default=0.0)
    bedrooms = fields.Integer('Bedrooms')
    living_area = fields.Integer('Living Area')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection('Garden Orientation', [('north', 'North'), ('west', 'West'), ('south', 'South'), ('east', 'East')], required=True, default='accounts')
