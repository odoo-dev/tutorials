from odoo import fields, models


class EstatePropertyOffer(models.Model):
    _inherit = 'estate.property.offer'

    property_sale_type = fields.Selection(related="property_id.property_sale_type")