from datetime import datetime

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

    @api.depends('product_id', 'product_uom', 'product_uom_qty', 'order_id.end_date', 'order_id.date_order')
    def _compute_price_unit(self):
        """Compute the unit price based on the subscription pricing rules."""
        all_continued = True

        for line in self:
            order = line.order_id
            
            if not order or not line.product_id or not order.plan_id or not order.pricelist_id:
                continue
            
            if not order.date_order or not order.end_date:
                continue
            
            pricelist_item = self.env["sale.subscription.pricing"].search([
                ('product_template_id', '=', line.product_id.product_tmpl_id.id),
                ('pricelist_id', '=', order.pricelist_id.id),
                ('plan_id', '=', order.plan_id.id)
            ], limit=1)
            
            if not pricelist_item:
                continue
            
            start_date = order.date_order.date() if isinstance(order.date_order, datetime) else order.date_order
            end_date = order.end_date.date() if isinstance(order.end_date, datetime) else order.end_date

            duration_vals = self.env["product.pricing"]._compute_duration_vals(start_date, end_date)
            unit = pricelist_item.plan_id.billing_period_unit
            duration = duration_vals.get(unit, 0)
            
            if duration >= pricelist_item.min_quantity:
                line.price_unit = pricelist_item._compute_price(
                    product=line.product_id,
                    quantity=duration,
                    uom=line.product_uom,
                    date=order.date_order,
                    currency=line.currency_id,
                )
                all_continued = False
        
        if all_continued:
            super()._compute_price_unit()
