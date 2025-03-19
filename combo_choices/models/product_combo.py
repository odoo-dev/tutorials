from odoo import _, api, fields, models


class ProductCombo(models.Model):
    _inherit = "product.combo"

    qty_free = fields.Integer(string="free")
    qty_max = fields.Integer(string="items")

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id) 
        params += ['qty_free','qty_max']
        return params