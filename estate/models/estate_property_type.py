from odoo import fields, models, api
class EstatePropertyType(models.Model):
    _name ="estate.property.type"
    _description = "Estate property Type Model"
    _order="sequence, name"
    name=fields.Char(required=True)
    property_ids=fields.One2many('estate.property','property_type_id',string="Properties")
    _sql_constraints=[('check_name','UNIQUE(name)',
    'The Property type name Mustt be Unique')]
    sequence=fields.Integer('Sequence', default=1)

    # avg =fields.Float(compute="_compute_avg_expected_price")
    # @api.depends("property_ids.expected_price")
    # def _compute_avg_expected_price(self):
    #     for record in self:
    #         record.avg=sum(record.property_ids.mapped("expected_price"))/len(record.property_ids.mapped("expected_price"))