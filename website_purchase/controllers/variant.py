from odoo import http
from odoo.http import request

class WebsiteSaleSellController(http.Controller):

    @http.route('/shop/cart/update_sell', type='json', auth='public', methods=['POST'], website=True)
    def update_sell_cart(self, product_id, sell_qty, **kwargs):
        if not product_id:
            return {'error': 'No product selected'}

        product = request.env['product.product'].browse(int(product_id))

        # Find the pricelist for selling
        pricelist = request.website.get_current_pricelist()
        sell_price = product.with_context(pricelist=pricelist.id).price_compute('list_price')[product.id]

        # Create a sale order for selling
        order = request.website.sale_get_order(force_create=True)
        order.write({'order_type': 'sell'})

        # Add product to sale order
        order_line = order.order_line.filtered(lambda l: l.product_id == product)
        if order_line:
            order_line.write({'product_uom_qty': order_line.product_uom_qty + float(sell_qty)})
        else:
            order.write({
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': float(sell_qty),
                    'price_unit': sell_price,
                })]
            })

        return {'success': True, 'order_id': order.id}
