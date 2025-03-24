from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestRentalPricelistRule(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.subscription_category = cls.env['product.category'].create({'name': 'Subscription Services'})

        cls.streaming_service_premium = cls.env['product.product'].create({
            'name': 'Streaming Service Premium Plan',
            'categ_id': cls.subscription_category.id,
            'standard_price': 12000,
            'list_price': 15000,
            'recurring_invoice': True,
        })

        cls.streaming_service_standard = cls.env['product.product'].create({
            'name': 'Streaming Service Standard Plan',
            'categ_id': cls.subscription_category.id,
            'standard_price': 9000,
            'list_price': 11000,
            'recurring_invoice': True,
        })

        cls.plan_month = cls.env['sale.subscription.plan'].create({
            'name': 'Monthly',
            'billing_period_value': 1,
            'billing_period_unit': 'month'
        })
        cls.plan_week = cls.env['sale.subscription.plan'].create({
            'name': 'Weekly',
            'billing_period_value': 1,
            'billing_period_unit': 'week'
        })
        cls.plan_year = cls.env['sale.subscription.plan'].create({
            'name': 'Yearly',
            'billing_period_value': 1,
            'billing_period_unit': 'year'
        })

        cls.subscription_pricelist = cls.env['product.pricelist'].create({'name': 'Subscription Pricelist'})      

        cls.pricing_item_1 = cls.env['sale.subscription.pricing'].create({
            'display_applied_on': '1_product',
            'product_tmpl_id': cls.streaming_service_premium.product_tmpl_id.id,
            'compute_price': 'percentage',
            'base': 'list_price',
            'price': 150,
            'percent_price': 10,
            'min_quantity': 2,
            'plan_id': cls.plan_month.id,
            'pricelist_id': cls.subscription_pricelist.id
        })

        cls.pricing_item_2 = cls.env['sale.subscription.pricing'].create({
            'display_applied_on': '1_product',
            'product_tmpl_id': cls.streaming_service_premium.product_tmpl_id.id,
            'compute_price': 'fixed',
            'price': 900,
            'fixed_price': 20000,
            'min_quantity': 2,
            'plan_id': cls.plan_week.id,
            'pricelist_id': cls.subscription_pricelist.id
        })

    def test_compute_price_unit_all_pricing_rules(self):
        """ Test _compute_price_unit with different recurrence intervals """
        partner = self.env.ref('base.res_partner_12')
        now = fields.Datetime.now()

        order_monthly = self.env['sale.order'].create({
            'partner_id': partner.id,
            'pricelist_id': self.subscription_pricelist.id,
            'date_order': now,
            'plan_id': self.plan_month.id,
            'end_date': now + relativedelta(months=2),
        })
        order_line_monthly = self.env['sale.order.line'].create({
            'order_id': order_monthly.id,
            'product_id': self.streaming_service_premium.id,
            'product_uom_qty': 2,
            'product_uom': self.streaming_service_premium.uom_id.id,
        })
        order_line_monthly._compute_price_unit()
        expected_monthly_price = self.streaming_service_premium.list_price * 0.90
        self.assertEqual(order_line_monthly.price_unit, expected_monthly_price, "Monthly pricing rule not applied correctly")

        order_weekly = self.env['sale.order'].create({
            'partner_id': partner.id,
            'pricelist_id': self.subscription_pricelist.id,
            'date_order': now,
            'plan_id': self.plan_week.id,
            'end_date': now + relativedelta(weeks=2),
        })
        order_line_weekly = self.env['sale.order.line'].create({
            'order_id': order_weekly.id,
            'product_id': self.streaming_service_premium.id,
            'product_uom_qty': 2,
            'product_uom': self.streaming_service_premium.uom_id.id,
        })
        order_line_weekly._compute_price_unit()
        self.assertEqual(order_line_weekly.price_unit, 20000, "Weekly pricing rule not applied correctly")

        order_yearly = self.env['sale.order'].create({
            'partner_id': partner.id,
            'pricelist_id': self.subscription_pricelist.id,
            'date_order': now,
            'plan_id': self.plan_year.id,
            'end_date': now + relativedelta(years=1),
        })
        order_line_yearly = self.env['sale.order.line'].create({
            'order_id': order_yearly.id,
            'product_id': self.streaming_service_standard.id,
            'product_uom_qty': 1,
            'product_uom': self.streaming_service_standard.uom_id.id,
        })
        order_line_yearly._compute_price_unit()
        self.assertEqual(order_line_yearly.price_unit, self.streaming_service_standard.list_price, "Yearly pricing rule not applied correctly")
