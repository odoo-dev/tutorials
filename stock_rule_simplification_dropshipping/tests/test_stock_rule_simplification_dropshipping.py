from odoo import Command
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestStockRuleSimplificationDropshipping(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResCompany = self.env['res.company']
        self.StockRule = self.env['stock.rule']
        self.MrpBom = self.env['mrp.bom']
        self.ProductProduct = self.env['product.product']
        self.ProductTemplate = self.env['product.template']

        self.product = self.ProductTemplate.create({
            'name': 'Test Product'
        })

        self.component = self.ProductProduct.create({
            'name': 'BOM Component',
        })

        self.subcontractor = self.env['res.partner'].create({
            'name': 'Test Subcontractor',
        })

        self.supplier = self.env['res.partner'].create({
            'name': 'Test Supplier',
        })

        self.dropship_route = self.env.ref('stock_dropshipping.route_drop_shipping', raise_if_not_found=False)
        self.subcontracting_route = self.env.ref('mrp_subcontracting_dropshipping.route_subcontracting_dropshipping', raise_if_not_found=False)

        self.company = self.ResCompany.create({'name': 'Test Company'})

        self.stock_rule = self.StockRule.create({
            'name': 'Subcontracting Rule',
            'route_id': self.subcontracting_route.id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        })

        self.env.company.dropship_subcontractor_pick_type_id.active = True

    def test_merge_dropship_rule(self):
        self.company._merge_dropship_rule()

        self.assertEqual(self.stock_rule.route_id, self.dropship_route)

        self.assertFalse(self.subcontracting_route.active)

        subcontracting_picking = self.env.company.dropship_subcontractor_pick_type_id
        self.assertFalse(subcontracting_picking.active)

    def test_resupply_order_creation(self):
        bom = self.MrpBom.create({
            'product_tmpl_id': self.product.id,
            'type': 'subcontract',
            'bom_line_ids': [(0, 0, {'product_id': self.component.id, 'product_qty': 1})],
            'subcontractor_ids': [(6, 0, [self.subcontractor.id])]
        })

        self.component.route_ids = [(4, self.dropship_route.id)]
        self.component.seller_ids = [(0, 0, {'partner_id': self.supplier.id})]

        purchase_order = self.env['purchase.order'].create({
            'partner_id': self.subcontractor.id,
            'order_line': [(
                Command.create({
                    'product_id': self.product.product_variant_id.id,
                    'product_uom_qty': 1,
                    'price_unit': 100,
                })
            )]
        })

        purchase_order.button_confirm()

        new_po_count = self.env['purchase.order.line'].search_count([('product_id', '=', self.component.id)])
        self.assertGreaterEqual(new_po_count, 1)
