from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('-at_install', 'post_install')
class TestSubscriptionPricelistRuleCreation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.subscription_category = cls.env['product.category'].create({'name': 'Subscription Products'})
        
        cls.subscription_pricelist = cls.env['product.pricelist'].create({'name': 'Subscription Pricelist',})      
        
        cls.streaming_service_premium = cls.env['product.product'].create({
            'name': 'Streaming Service Premium Plan',
            'categ_id': cls.subscription_category.id,
            'standard_price': 12000,
            'list_price': 15000,
            'recurring_invoice': True,
        }).product_tmpl_id

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

    def test_create_subscription_pricing_rule(self):
        """ Test the creation of subscription pricing rules """

        Pricing = self.env['sale.subscription.pricing']

        daily_pricing = Pricing.create({
            'display_applied_on': '1_product',
            'product_tmpl_id': self.streaming_service_premium.id,
            'compute_price': 'percentage',
            'base': 'list_price',
            'price': 150,  
            'percent_price': 10,  
            'min_quantity': 2,
            'plan_id': self.plan_month.id,
            'pricelist_id': self.subscription_pricelist.id
        })
        self.assertEqual(daily_pricing.product_tmpl_id, self.streaming_service_premium, "Daily pricing rule not applied correctly")
        self.assertEqual(daily_pricing.compute_price, 'percentage', "Daily pricing rule not applied correctly")
        
        weekly_pricing = Pricing.create({
            'display_applied_on': '2_product_category',
            'categ_id': self.subscription_category.id,
            'compute_price': 'fixed',
            'fixed_price': 20000,  
            'min_quantity': 2,
            'plan_id': self.plan_week.id,
            'pricelist_id': self.subscription_pricelist.id
        })
        self.assertEqual(weekly_pricing.categ_id, self.subscription_category, "Weekly pricing rule not applied correctly")

        with self.assertRaises(UserError):
            Pricing.create({
                'display_applied_on': '2_product_category',
                'categ_id': None,
                'compute_price': 'fixed',
                'fixed_price': 20000,
                'min_quantity': 2,
                'plan_id': self.plan_year.id,
                'pricelist_id': self.subscription_pricelist.id
            })
