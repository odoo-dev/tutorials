from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class LastSoldProducts(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(LastSoldProducts, cls).setUpClass()

        cls.product_1 = cls.env['product.product'].create({
            'name': 'Test Product1',
            'purchase_method': 'purchase'
        })
        cls.product_2 = cls.env['product.product'].create({
            'name': 'Test Product2',
            'purchase_method': 'purchase'
        })       
        cls.partner_1 = cls.env['res.partner'].create({'name': 'Test Customer'})

        cls.purchase_order_1 = cls.env['purchase.order'].create({
            'partner_id': cls.partner_1.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product_1.name,
                    'product_id': cls.product_1.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.product_1.uom_id.id,
                    'price_unit': cls.product_1.list_price,
                })
            ],
        })
        cls.purchase_order_1.button_confirm()
        cls.purchase_order_1.action_view_picking()
        cls.purchase_order_1.action_create_invoice()
        cls.test_bill_1 = cls.env['account.move'].search([('invoice_origin', '=', cls.purchase_order_1.name)])
        cls.env.cr.execute(""" UPDATE account_move set invoice_date = '%s' WHERE id = '%s'""" % ('2025-01-10', cls.test_bill_1.id))

        cls.purchase_order_2 = cls.env['purchase.order'].create({
            'partner_id': cls.partner_1.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product_2.name,
                    'product_id': cls.product_2.id,
                    'product_uom_qty': 1,
                    'product_uom': cls.product_2.uom_id.id,
                    'price_unit': cls.product_2.list_price,
                })
            ],
        })
        cls.purchase_order_2.button_confirm()
        cls.purchase_order_2.action_view_picking()
        cls.purchase_order_2.action_create_invoice()
        cls.test_bill_2 = cls.env['account.move'].search([('invoice_origin', '=', cls.purchase_order_2.name)])
        cls.env.cr.execute(""" UPDATE account_move set invoice_date = '%s' WHERE id = '%s'""" % ('2025-02-10', cls.test_bill_2.id))

        cls.test_journal_type_sale = cls.env['account.journal'].search([('type', '=', 'sale')], limit=1)

        cls.sale_order_1 = cls.env['sale.order'].create({
            'partner_id': cls.partner_1.id,
            'order_line': [(0, 0, {
                'name': cls.product_1.name,
                'product_id': cls.product_1.id,
                'product_uom_qty': 1,
                'product_uom': cls.product_1.uom_id.id,
                'price_unit': cls.product_1.list_price,
            })],
        })
        cls.sale_order_1.action_confirm()

        so_context = {
            'active_model': 'sale.order',
            'active_ids': [cls.sale_order_1.id],
            'active_id': cls.sale_order_1.id,
            'default_journal_id': cls.test_journal_type_sale.id,
        }
        cls.test_downpayment = cls.env['sale.advance.payment.inv'].with_context(so_context).create({
            'advance_payment_method': 'percentage',
            'amount': 50,
        })
        cls.test_downpayment.create_invoices()

        cls.test_invoice_1 = cls.env['account.move'].search([('invoice_origin', '=', cls.sale_order_1.name)])
        cls.env.cr.execute(""" UPDATE account_move set invoice_date = '%s' WHERE id = '%s'""" % ('2025-01-10', cls.test_bill_1.id))

        cls.test_sale_order_2 = cls.env['sale.order'].create({
            'partner_id': cls.partner_1.id,
            'order_line': [(0, 0, {
                'name': cls.product_2.name,
                'product_id': cls.product_2.id,
                'product_uom_qty': 1,
                'product_uom': cls.product_2.uom_id.id,
                'price_unit': cls.product_2.list_price,
            })],
        })
        cls.test_sale_order_2.action_confirm()

        so_context['active_id'] = cls.test_sale_order_2.id
        cls.test_downpayment = cls.env['sale.advance.payment.inv'].with_context(so_context).create({
            'advance_payment_method': 'percentage',
            'amount': 50,
        })
        cls.test_downpayment.create_invoices()

        cls.test_invoice_2 = cls.env['account.move'].search([('invoice_origin', '=', cls.test_sale_order_2.name)])
        cls.env.cr.execute(""" UPDATE account_move set invoice_date = '%s' WHERE id = '%s'""" % ('2025-02-10', cls.test_bill_2.id))

    def test_product_variant_in_sale_order(self):
        """Test that products in the sale order dropdown are sorted by last invoice date."""
        so_context = {
            'partner_id': self.partner_1.id,
            'order_type': 'sale'
        }
        res = self.env['product.product'].with_context(so_context).name_search(
            name='', args=[('id', 'in', [self.product_1.id, self.product_2.id])]
        )
        res_ids = [r[0] for r in res]

        self.assertEqual(res_ids[0], self.product_1.id, "Latest invoiced product should be first")
        self.assertEqual(res_ids[1], self.product_2.id, "Older invoiced product should be second")

    def test_product_variant_in_purchase_order(self):
        po_context = {
            'partner_id': self.partner_1.id,
            'order_type': 'purchase'
        }
        res = self.env['product.product'].with_context(po_context).name_search(
            name='', args=[('id', 'in', [self.product_1.id, self.product_2.id])]
        )
        res_ids = [r[0] for r in res]
        self.assertEqual(self.product_1.id, res_ids[0])
        self.assertEqual(self.product_2.id, res_ids[1])
