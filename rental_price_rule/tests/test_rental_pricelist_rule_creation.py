from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('-at_install', 'post_install')
class TestRentalPricelistRuleCreation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rental_category = cls.env['product.category'].create({'name': 'Rental Products'})

        cls.conference_hall = cls.env['product.product'].create({
            'name': 'Conference Hall',
            'categ_id': cls.rental_category.id,
            'standard_price': 12000,
            'list_price': 15000,
            'rent_ok': True,
        })  

        cls.town_hall = cls.env['product.product'].create({
            'name': 'Town Hall',
            'categ_id': cls.rental_category.id,
            'standard_price': 9000,
            'list_price': 11000,
            'rent_ok': True,
        })

        cls.daily_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Daily', 'duration': 1, 'unit': 'day'})
        cls.weekly_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Weekly', 'duration': 1, 'unit': 'week'})
        cls.monthly_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Monthly', 'duration': 1, 'unit': 'month'})
        cls.yearly_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Yearly', 'duration': 1, 'unit': 'year'})

        cls.rental_pricelist = cls.env['product.pricelist'].create({'name': 'Rental Pricelist'})      
  
    def test_create_rental_pricing_rule(self):
        """ Test the creation of rental pricing rules """

        Pricing = self.env['product.pricing']
        
        daily_pricing = Pricing.create({
            'display_applied_on': '1_product',
            'product_tmpl_id': self.conference_hall.product_tmpl_id.id,
            'compute_price': 'percentage',
            'base': 'list_price',
            'price': 150,
            'percent_price': 10,
            'min_quantity': 2,
            'recurrence_id': self.daily_recurrence.id,
            'pricelist_id': self.rental_pricelist.id
        })
        self.assertEqual(daily_pricing.product_id, self.conference_hall, "Daily pricing rule not applied correctly")
        self.assertEqual(daily_pricing.compute_price, 'percentage', "Daily pricing rule not applied correctly")
        
        weekly_pricing = Pricing.create({
            'display_applied_on': '2_product_category',
            'categ_id': self.rental_category.id,
            'compute_price': 'fixed',
            'price': 900,
            'fixed_price': 20000,
            'min_quantity': 2,
            'recurrence_id': self.weekly_recurrence.id,
            'pricelist_id': self.rental_pricelist.id
        })
        self.assertEqual(weekly_pricing.categ_id, self.rental_category, "Weekly pricing rule not applied correctly")
        
        monthly_pricing = Pricing.create({
            'display_applied_on': '1_product',
            'product_tmpl_id': None,
            'compute_price': 'fixed',
            'price': 900,
            'fixed_price': 20000,
            'min_quantity': 2,
            'recurrence_id': self.monthly_recurrence.id,
            'pricelist_id': self.rental_pricelist.id
        })
        self.assertEqual(daily_pricing.product_id, self.conference_hall, "Daily pricing rule not applied correctly")

        with self.assertRaises(UserError):
            yearly_pricing = Pricing.create({
                'display_applied_on': '2_product_category',
                'categ_id': None,
                'compute_price': 'fixed',
                'price': 900,
                'fixed_price': 20000,
                'min_quantity': 2,
                'recurrence_id': self.monthly_recurrence.id,
                'pricelist_id': self.rental_pricelist.id
            })        
        