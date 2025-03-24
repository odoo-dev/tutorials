from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_product_variant_mode = fields.Selection(
        [
            ('matrix', 'Variant Grid Entry'),
            ('configurator', 'Product Configurator')
        ],
        string="Purchase Product Variant Mode",
        default='matrix',
        help="Choose how product variants should be added to purchase orders.",
        config_parameter="purchase.purchase_product_variant_mode"
    )

    api.onchange('module_purchase_product_matrix')
    def _onchange_module_purchase_product_matrix(self):
        if not self.module_purchase_product_matrix and self.purchase_product_variant_mode == 'configurator':
            self.purchase_product_variant_mode = 'matrix'
