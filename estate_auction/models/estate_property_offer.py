from odoo import api, models, _
from odoo.exceptions import UserError


class EstatePropertyOfferAuction(models.Model):
    _inherit = 'estate.property.offer'

    @api.model_create_multi
    def create(self, vals_list):
        property_obj = self.env['estate.property'].browse(vals_list[0]['property_id'])
        if vals_list[0]['price'] < property_obj.expected_price:
            raise UserError(_("offer price is lower than expected price"))
        return models.Model.create(self, vals_list)
