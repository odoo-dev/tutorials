import math
from datetime import date

from odoo import api, fields, models


PERIOD_RATIO = {
    'hour': 1,
    'day': 24,
    'week': 24 * 7,
    'month': 24 * 31,
    'year': 24 * 31 * 12,
}

class RentalPricingRules(models.Model):
    _name = "product.pricing"
    _inherit = ["product.pricing", "product.pricelist.item"]

    is_rental_product = fields.Boolean(related="product_tmpl_id.rent_ok")
    product_template_id = fields.Many2one("product.template")
    product_id_id = fields.Integer(related="product_template_id.id")

    compute_price = fields.Selection(
        selection=[
            ('percentage', "Discount"),
            ('formula', "Formula"),
            ('fixed', "Fixed Price"),
        ],
        help="Use the discount rules and activate the discount settings "
             "in order to show discount to the customer.",
        index=True, 
        default='percentage', 
        required=True
    )
    
    
    def create(self, vals_list):
        records = super().create(vals_list)  # Call the parent method
        for record in records:
            product = self.env['product.product'].search(
                [('product_tmpl_id', '=', record.product_tmpl_id.id)], 
                limit=1
            )
            if product:
                record.product_id = product.id
                record.product_template_id = product.product_tmpl_id.id
                record.product_tmpl_id = product.product_tmpl_id
                
            # breakpoint()
        return records

    def _compute_price_rental(self, product, quantity, uom, date, currency):
        """Compute the price for a specified duration of the current pricing rental rule.
        :return float: price
        """
        self.ensure_one()
        
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()

        product_uom = product.uom_id
        convert = lambda p: product_uom._compute_price(p, uom) if product_uom != uom else p
        
        if self.compute_price == 'fixed':
            price = convert(self.fixed_price)
        elif self.compute_price == 'percentage':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            price = base_price - (base_price * (self.percent_price / 100)) or 0.0
        elif self.compute_price == 'formula':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            price_limit = base_price
            price = base_price - (base_price * (self.price_discount / 100)) or 0.0

            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)

            if self.price_surcharge:
                price += convert(self.price_surcharge)

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))
        else:
            price = self._compute_base_price(product, quantity, uom, date, currency)

        return price
