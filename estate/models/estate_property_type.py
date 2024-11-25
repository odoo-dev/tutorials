from odoo import models, fields,api

class EstatePropertyType(models.Model):
    _name ="estate.property.type"
    _description = "Estate property Type Model"
    _order="sequence,name desc"
    _sql_constraints = [('name_uniq', "unique(name)", "The name must be unique.")]
    name= fields.Char(required=True) 
    sequence= fields.Integer('Sequence', default=1, help="Used to order Properties.")
    property_ids= fields.One2many(
        comodel_name='estate.property',
        inverse_name='property_type_id',
        string='Properties')
    offer_ids= fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_type_id',
        string='Offers')
    offer_count = fields.Integer(compute='_compute_offer_count')  
    
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
        return True 