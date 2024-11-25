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
    offer_ids=fields.One2many('estate.property.offer' ,'property_type_id')
    offer_count=fields.Integer(compute="_compute_number_of_offers")

    @api.depends("offer_ids")
    def _compute_number_of_offers(self):
        for record in self:
            record.offer_count=len(record.offer_ids)

    # define action for the offer button to show number of offers 
    # just to  hceck it work or not for learning. 
    # avg =fields.Float(compute="_compute_avg_expected_price")
    # @api.depends("property_ids.expected_price")
    # def _compute_avg_expected_price(self):
    #     for record in self:
    #         record.avg=sum(record.property_ids.mapped("expected_price"))/len(record.property_ids.mapped("expected_price"))