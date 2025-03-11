from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestStockRuleSimplificationMRP(TransactionCase):
    def setUp(self):
        super().setUp()
        self.MrpBom = self.env['mrp.bom']
        self.ProductTemplate = self.env['product.template']
        self.SaleOrder = self.env['sale.order']
        self.manufacture_route = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        self.mto_route = self.env.ref('stock.route_warehouse0_mto', raise_if_not_found=False)

        self.product = self.ProductTemplate.create({
            'name': 'Test Product',
            'purchase_ok': False,
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Test Supplier'
        })

    def test_manufacture_route(self):
        bom1 = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'phantom'
        })

        self.assertNotIn(self.manufacture_route, self.product.route_ids)

        bom2 = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'normal'
        })

        self.assertIn(self.manufacture_route, self.product.route_ids)

    def test_unlink_bom_removes_manufacture_route(self):
        bom = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'normal'
        })

        bom.unlink()
        self.assertNotIn(self.manufacture_route, self.product.route_ids)

    def test_manufacture_order_creation(self):
        bom = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'normal'
        })
        self.assertIn(self.manufacture_route, self.product.route_ids)

        self.mto_route.active = True
        self.product.route_ids = [(4, self.mto_route.id)]

        sale_order = self.SaleOrder.create({
            'partner_id': self.partner.id,
            'order_line': [(
                Command.create({
                    'product_id': self.product.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 100,
                })
            )]
        })

        sale_order.action_confirm()
        self.assertGreaterEqual(sale_order.mrp_production_count, 1)

        self.mto_route.active = False
