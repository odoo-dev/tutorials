import math

from odoo import api, fields, models


PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7,
    'month': 24 * 31,
    'year': 24 * 31 * 12,
}

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('start_date', 'return_date', 'product_id', 'product_uom_qty')
    def _compute_price_unit(self):
        Pricing = self.env['product.pricing']

        for line in self:
            order = line.order_id
            product = line.product_id

            if not order or not line.start_date or not line.return_date or not product:
                continue

            pricing = product._get_best_pricing_rule(
                start_date=line.start_date,
                end_date=line.return_date,
                pricelist=order.pricelist_id,
                currency=order.currency_id
            )

            if not pricing or pricing.recurrence_id.duration <= 0:
                continue

            duration_vals = Pricing._compute_duration_vals(line.start_date, line.return_date)
            unit = pricing.recurrence_id.unit
            duration = duration_vals.get(unit, 0)

            converted_duration = (
                math.ceil(duration / pricing.recurrence_id.duration)
                if unit == pricing.recurrence_id.unit
                else math.ceil((duration * PERIOD_RATIO[unit]) / (pricing.recurrence_id.duration * PERIOD_RATIO[pricing.recurrence_id.unit]))
            )
            
            if pricing and pricing.min_quantity <= converted_duration:
                price = pricing._compute_price_rental(
                    product=product.with_context(**line._get_product_price_context()),
                    quantity=converted_duration,
                    uom=line.product_uom,
                    date=order.date_order,
                    currency=line.currency_id,
                )
                line.price_unit = price * converted_duration
                return
            else:
                line.price_unit = pricing.price if pricing else product.list_price
                return
                
        super()._compute_price_unit()
