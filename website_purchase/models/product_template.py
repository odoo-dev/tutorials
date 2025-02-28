from odoo import models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(
        self, combination=False, product_id=False, add_qty=1.0,
        parent_combination=False, only_template=False, sell_qty=1.0,
    ):
        # Get the standard combination info
        combination_info = super()._get_combination_info(
            combination=combination,
            product_id=product_id,
            add_qty=add_qty,
            parent_combination=parent_combination,
            only_template=only_template,
        )

        # Add sell_qty for frontend tracking
        combination_info['sell_qty'] = sell_qty

        return combination_info
