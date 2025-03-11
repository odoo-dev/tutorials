from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestStockRuleSimplificationPurchase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductTemplate = self.env['product.template']
        self.ResPartner = self.env['res.partner']
        self.SaleOrder = self.env['sale.order']
        self.buy_route = self.env.ref('purchase_stock.route_warehouse0_buy', raise_if_not_found=False)
        self.mto_route = self.env.ref('stock.route_warehouse0_mto', raise_if_not_found=False)

        self.product = self.ProductTemplate.create({
            'name': 'Test Product',
            'purchase_ok': False
        })

        self.supplier = self.ResPartner.create({
            'name': 'Test Supplier'
        })

    def test_check_buy_route(self):
        self.assertNotIn(self.buy_route, self.product.route_ids)

        self.product.purchase_ok = True
        self.assertNotIn(self.buy_route, self.product.route_ids)

        self.product.seller_ids = [(0, 0, {'partner_id': self.supplier.id})]
        self.assertIn(self.buy_route, self.product.route_ids)

        self.product.purchase_ok = False
        self.assertNotIn(self.buy_route, self.product.route_ids)

        self.product.purchase_ok = True
        self.assertIn(self.buy_route, self.product.route_ids)

        self.product.seller_ids = [(5, 0, 0)]
        self.assertNotIn(self.buy_route, self.product.route_ids)

    def test_purchase_order_creation(self):
        self.product.purchase_ok = True
        self.product.seller_ids = [(0, 0, {'partner_id': self.supplier.id})]
        self.assertIn(self.buy_route, self.product.route_ids)

        self.mto_route.active = True
        self.product.route_ids = [(4, self.mto_route.id)]

        sale_order = self.SaleOrder.create({
            'partner_id': self.supplier.id,
            'order_line': [(
                Command.create({
                    'product_id': self.product.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 100,
                })
            )]
        })

        sale_order.action_confirm()
        self.assertGreaterEqual(sale_order.purchase_order_count, 1)

        self.mto_route.active = False
