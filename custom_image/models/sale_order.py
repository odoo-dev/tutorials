from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_order_line_values(
        self, product_id, quantity, linked_line_id=False,
        no_variant_attribute_value_ids=None, product_custom_attribute_values=None,
        combo_item_id=None,
        **kwargs
    ):
        values = super()._prepare_order_line_values(
            product_id, quantity, linked_line_id,
            no_variant_attribute_value_ids, product_custom_attribute_values,
            combo_item_id,
            **kwargs
        )

        custom_image = kwargs.get('custom_image')
        values['custom_image'] = custom_image

        return values

    def _prepare_order_line_update_values(self, order_line, quantity, linked_line_id=False, **kwargs):
        values = super()._prepare_order_line_update_values(order_line, quantity, linked_line_id, **kwargs)

        custom_image = kwargs.get('custom_image')

        if custom_image:
            values['custom_image'] = custom_image

        return values
