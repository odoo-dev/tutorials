from odoo import fields, models
class EstatePropertyType(models.Model):
    _name ="estate.property.type"
    _description = "Estate property Type Model"
    name=fields.Char(required=True)
    property_ids=fields.One2many('estate.property','property_type_id',string="Properties")
    _sql_constraints=[('check_name','UNIQUE(name)',
    'The Property type name Mustt be Unique')]

    # defining extra fields to add the view list
    expected_price=fields.Float(related="property_ids.expected_price")
    # state=fields.Float(related=property_ids.state)
   