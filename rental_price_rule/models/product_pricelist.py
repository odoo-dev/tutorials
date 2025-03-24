from odoo import api, fields, models

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_pricing_rules(self, products, date, **kwargs):
        """ Fetch applicable pricing rules for the given products and date """

        self.ensure_one()

        if not self:
            return self.env['product.pricing']

        return self.env['product.pricing'].with_context(active_test=False).search(
            self._get_applicable_pricing_rules_domain(products=products, date=date, **kwargs)
        ).with_context(self.env.context)

    def _get_applicable_pricing_rules_domain(self, products, date, **kwargs):
        """ Construct the domain to search for applicable pricing rules """

        self.ensure_one()

        if products._name == 'product.template':
            templates_domain = ('product_tmpl_id', 'in', products.ids)
            products_domain = ('product_id.product_tmpl_id', 'in', products.ids)
        else:
            templates_domain = ('product_tmpl_id', 'in', products.product_tmpl_id.ids)
            products_domain = ('product_id', 'in', products.ids)

        return [
            ('pricelist_id', '=', self.id),
            '|', ('categ_id', '=', False), ('categ_id', 'parent_of', products.categ_id.ids),
            '|', ('product_tmpl_id', '=', False), templates_domain,
            '|', ('product_id', '=', False), products_domain,
            '|', ('date_start', '=', False), ('date_start', '<=', date),
            '|', ('date_end', '=', False), ('date_end', '>=', date),
        ]
    
    def _compute_pricing_rule(
        self, products, quantity, currency=None, uom=None, date=False, compute_price=True, **kwargs
    ):
        """ Similar logic to _compute_price_rule but applied to product.pricing """

        self.ensure_one()
        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()

        if not products:
            return {}

        if not date:
            date = fields.Datetime.now()

        pricing_rules = self._get_applicable_pricing_rules(products, date, **kwargs)

        results = {}
        for product in products:
            suitable_rule = self.env['product.pricing']

            product_uom = product.uom_id
            target_uom = uom or product_uom

            if target_uom != product_uom:
                qty_in_product_uom = target_uom._compute_quantity(
                    quantity, product_uom, raise_if_failure=False
                )
            else:
                qty_in_product_uom = quantity

            for rule in pricing_rules:
                if rule._is_applicable_for(product, qty_in_product_uom):
                    suitable_rule = rule
                    break

            if compute_price:
                price = suitable_rule._compute_price_rental(
                    product, quantity, target_uom, date=date, currency=currency
                )
            else:
                price = 0.0

            results[product.id] = (price, suitable_rule.id)

        return results
    