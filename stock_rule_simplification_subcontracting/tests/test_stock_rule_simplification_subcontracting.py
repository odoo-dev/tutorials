from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestStockRuleSimplificationSubcontracting(TransactionCase):
    def setUp(self):
        super().setUp()
        self.MrpBom = self.env['mrp.bom']
        self.ProductProduct = self.env['product.product']
        self.ProductTemplate = self.env['product.template']
        self.resupply_route = self.env.ref('mrp_subcontracting.route_resupply_subcontractor_mto', raise_if_not_found=False)

        self.product = self.ProductTemplate.create({
            'name': 'Test Product'
        })

        self.component = self.ProductProduct.create({
            'name': 'BOM Component',
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Test Subcontractor',
        })


    def test_create_subcontract_bom_adds_resupply_route(self):
        self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'subcontract',
            'bom_line_ids': [(0, 0, {'product_id': self.component.id, 'product_qty': 1})]
        })

        self.assertIn(self.resupply_route, self.component.product_tmpl_id.route_ids)

    def test_write_subcontract_bom_adds_resupply_route(self):
        bom = self.MrpBom.create({'product_tmpl_id': self.product.id, 'type': 'normal'})
        bom.write({'type': 'subcontract', 'bom_line_ids': [(0, 0, {'product_id': self.component.id, 'product_qty': 1})]})

        self.assertIn(self.resupply_route, self.component.product_tmpl_id.route_ids)

    def test_unlink_subcontract_bom_removes_resupply_route(self):
        bom = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'subcontract',
            'bom_line_ids': [(0, 0, {'product_id': self.component.id, 'product_qty': 1})]
        })

        bom.unlink()
        self.assertNotIn(self.resupply_route, self.component.product_tmpl_id.route_ids)

    def test_resupply_order_creation(self):
        bom = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'subcontract',
            'bom_line_ids': [(0, 0, {'product_id': self.component.id, 'product_qty': 1})],
            'subcontractor_ids': [(6, 0, [self.partner.id])]
        })

        self.assertIn(self.resupply_route, self.component.product_tmpl_id.route_ids)

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(
                Command.create({
                    'product_id': self.product.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 100,
                })
            )]
        })

        purchase_order.button_confirm()
        self.assertGreaterEqual(purchase_order.subcontracting_resupply_picking_count, 1)
