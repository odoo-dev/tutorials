from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('purchase_ok', 'seller_ids')
    def _compute_route_ids(self):
        buy_route = self.env.ref('purchase_stock.route_warehouse0_buy', raise_if_not_found=False)

        for product in self:
            if buy_route:
                if product.purchase_ok and product.seller_ids:
                    if buy_route.id not in product.route_ids.ids:
                        product.route_ids = [(4, buy_route.id)]
                else:
                    product.route_ids = [(3, buy_route.id)]

        return super()._compute_route_ids()
