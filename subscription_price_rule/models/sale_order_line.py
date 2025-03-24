from odoo import api, models, fields, tools
import datetime

PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7,
    'month': 24 * 31,
    'year': 24 * 31 * 12,
}

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            order = line.order_id  # Fetch order directly from the line

            # Ensure order exists
            if not order:
                continue

            # Fetch the pricelist item
            pricelist_item = self.env["sale.subscription.pricing"].search([
                ('product_template_id', '=', line.product_template_id.id),
                ('pricelist_id', '=', order.pricelist_id.id),
                ('plan_id', '=', order.plan_id.id)
            ], limit=1)

            if not pricelist_item:
                continue
            if not order.date_order or not order.end_date:
                continue  # Skip computation if dates are missing
            
            # Ensure both values are datetime.date
            start_date = order.date_order.date() if isinstance(order.date_order, datetime.datetime) else order.date_order
            end_date = order.end_date.date() if isinstance(order.end_date, datetime.datetime) else order.end_date

            duration_vals = self.env["product.pricing"]._compute_duration_vals(start_date, end_date)
            unit = pricelist_item.plan_id.billing_period_unit
            duration = duration_vals.get(unit, 0)

            price = pricelist_item._compute_price(
                product=line.product_id.with_context(**line._get_product_price_context()),
                quantity=duration,
                uom=line.product_uom,
                date=order.date_order,
                currency=line.currency_id,
            )
            
            # Assign computed price to line
            line.price_unit = price
            return

        
        super()._compute_price_unit()
            
