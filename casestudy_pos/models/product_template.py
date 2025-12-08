from odoo import models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def get_product_info_pos(self, price, quantity, pos_config_id, product_variant_id=False):
        product_info = super().get_product_info_pos(price, quantity, pos_config_id, product_variant_id)
        product_info.update(
            weight=self.weight,
            weight_uom_name=self.weight_uom_name,
            volume=self.volume,
            volume_uom_name=self.volume_uom_name
        )
        return product_info