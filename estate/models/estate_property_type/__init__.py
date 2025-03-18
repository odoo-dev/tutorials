from odoo import fields, models

class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real estate property type"
    _order = "name"

    name = fields.Char(required = True)
    sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'The property type name must be unique.')
    ]

    
    property_ids = fields.One2many("estate.property", "property_type_id", string = "Properties")
    
class PropertyTypeLine(models.Model):
    _name = "estate.property.type.line"
    _description = "Real estate property type line"

    model_id = fields.Many2one("estate.property.type")
    name = fields.Char("Title")
    expected_price = fields.Float("Expected Price")
    state = fields.Selection([
        ("new", "New"),
        ("offer_received", "Offer Received"),
        ("offer_accepted", "Offer Accepted"),
        ("sold", "Sold"),
        ("canceled", "Canceled")
    ], string="Status", required=True, copy=False, default="new")
