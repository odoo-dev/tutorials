import math

from odoo import api, models, fields


PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7,
    'month': 24 * 31,
    'year': 24 * 31 * 12,
}

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    rental_pricelist_item_id = fields.Many2one(
        comodel_name="product.pricing",
        compute='_compute_rental_pricelist_item_id')

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_rental_pricelist_item_id(self):
        for line in self:
            if not line._is_valid_rental_line():
                line.rental_pricelist_item_id = False
                continue
            
            line.rental_pricelist_item_id = line.product_id._get_best_pricing_rule(
                start_date=line.start_date,
                end_date=line.return_date,
                pricelist=line.order_id.pricelist_id,
                currency=line.order_id.currency_id
            )
    
    def _is_valid_rental_line(self):
        return self.product_id and not self.display_type and self.order_id and self.order_id.pricelist_id and self.return_date and self.start_date and self.product_id.rent_ok
    
    def _compute_converted_duration(self):
        pricelist_item = self.rental_pricelist_item_id
        duration_vals = pricelist_item._compute_duration_vals(self.start_date, self.return_date)
        unit = pricelist_item.recurrence_id.unit
        duration = duration_vals.get(unit, 0)
        return math.ceil((duration * PERIOD_RATIO[unit]) / 
                         (pricelist_item.recurrence_id.duration * PERIOD_RATIO[pricelist_item.recurrence_id.unit]))

    def _compute_rental_price(self, converted_duration):
        return self.rental_pricelist_item_id._compute_price_rental(
            product=self.product_id.with_context(**self._get_product_price_context()),
            quantity=converted_duration,
            uom=self.product_uom,
            date=self.order_id.date_order,
            currency=self.currency_id,
        )
        
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_discount(self):
        Pricing = self.env['product.pricing']
        discount_enabled = Pricing._is_discount_feature_enabled()

        rental_lines = self.filtered(lambda l: l._is_valid_rental_line() and discount_enabled)
        non_rental_lines = self - rental_lines

        for line in rental_lines:
            if not (line.rental_pricelist_item_id and line.rental_pricelist_item_id._show_discount()):
                continue
            
            converted_duration = line._compute_converted_duration()
            pricelist_price = line._compute_rental_price(converted_duration)
            base_price = line._get_pricelist_price_before_discount()
            
            if base_price != 0:
                discount = (base_price - pricelist_price) / base_price * 100
                if discount:
                    line.discount = discount

        if non_rental_lines:
            super()._compute_discount()

    
    def _get_pricelist_price(self):
        self.ensure_one()
        if not self._is_valid_rental_line():
            return super()._get_pricelist_price()
        
        converted_duration = self._compute_converted_duration()
        if self.rental_pricelist_item_id.min_quantity <= converted_duration:
            price = self._compute_rental_price(converted_duration)
            base_price = self._get_pricelist_price_before_discount()
            return max(base_price, price) if self.rental_pricelist_item_id._show_discount() else price
        return self.rental_pricelist_item_id.price

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        rental_lines = self.filtered(lambda l: l._is_valid_rental_line())
        non_rental_lines = self - rental_lines

        for line in rental_lines:
            if not line.order_id:
                continue

            converted_duration = line._compute_converted_duration()

            if line.technical_price_unit not in (0.0, line.price_unit) or line.qty_invoiced > 0:
                continue

            price = line._get_display_price() * converted_duration
            line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
                price,
                product_taxes=line.product_id.taxes_id.filtered(lambda tax: tax.company_id == line.env.company),
                fiscal_position=line.order_id.fiscal_position_id,
            )
            line.technical_price_unit = line.price_unit

        if non_rental_lines:
            super()._compute_price_unit()
