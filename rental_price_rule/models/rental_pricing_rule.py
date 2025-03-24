from datetime import date

from odoo import api, fields, models, tools
from odoo.exceptions import UserError


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

    
    period_unit = fields.Char(related="recurrence_id.duration_display")
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

    @api.onchange('product_template_id')
    def _onchange_template_id(self):
        self.product_tmpl_id = self.product_template_id
        
    @api.model_create_multi
    def create(self, vals_list):
        records = self.env[self._name]
        Product = self.env['product.product']
        Category = self.env['product.category']
        
        for vals in vals_list:
            vals_copy = vals.copy()
            display_on = vals.get('display_applied_on')
            categ_id = vals.get('categ_id')
            product_tmpl_id = vals.get('product_tmpl_id')
            
            if display_on == '2_product_category' and categ_id:
                category = Category.browse(categ_id)
                if not category.exists():
                    raise UserError("Selected category does not exist.")
                
                products = Product.search([
                    ('categ_id', '=', category.id),
                    ('rent_ok', '=', True)
                ])
            elif display_on == '1_product' and product_tmpl_id:
                products = Product.search([
                    ('product_tmpl_id', '=', product_tmpl_id),
                    ('rent_ok', '=', True)
                ], limit=1)
            elif display_on == '1_product':
                products = Product.search([
                    ('rent_ok', '=', True)
                ])
            else:
                raise UserError("You cannot create a time-based rule for a non-rentable category.")
            
            if not products:
                raise UserError("You cannot create a time-based rule for non-rentable products.")
            
            for product in products:
                vals_copy.update({
                    'product_id': product.id,
                    'product_template_id': product.product_tmpl_id.id,
                    'product_tmpl_id': product.product_tmpl_id.id
                })
                records += super().create([vals_copy])
        
        return records
    
    def _compute_price_rental(self, product, quantity, uom, date, currency):
        """Compute the price for a specified duration of the current pricing rental rule.
        :return float: price
        """        
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()
        
        Pricing = self.env["product.pricing"]

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
    
    def _compute_base_price(self, product, quantity, uom, date, currency):
        """ Compute the base price for a given rule

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: currency in which the returned price must be expressed

        :returns: base price, expressed in provided pricelist currency
        :rtype: float
        """
        currency.ensure_one()
        
        rule_base = self.base or 'list_price'
        pricing = self.env["product.pricing"]
        if rule_base == 'pricelist' and self.base_pricelist_id:
            price = self.base_pricelist_id._compute_pricing_rule(
                product, quantity, currency=self.base_pricelist_id.currency_id, uom=uom, date=date
            )[product.id][0]
            src_currency = self.base_pricelist_id.currency_id
        elif rule_base == "standard_price":
            src_currency = product.cost_currency_id
            price = product._price_compute(rule_base, uom=uom, date=date)[product.id]
        else: # list_price
            src_currency = product.currency_id
            price = product._price_compute(rule_base, uom=uom, date=date)[product.id]

        if src_currency != currency:
            price = src_currency._convert(price, currency, self.env.company, date, round=False)
        
        return price
