from datetime import timedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestRentalPricelistRule(TransactionCase):

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

        cls.daily_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Daily', 'duration': 1, 'unit': 'day'})
        cls.weekly_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Weekly', 'duration': 1, 'unit': 'week'})
        cls.monthly_recurrence = cls.env['sale.temporal.recurrence'].create({'name': 'Monthly', 'duration': 1, 'unit': 'month'})

        cls.rental_pricelist = cls.env['product.pricelist'].create({'name': 'Rental Pricelist'})

        cls.pricing_item_1 = cls.env['product.pricing'].create({
            'display_applied_on': '1_product',
            'product_tmpl_id': cls.conference_hall.product_tmpl_id.id,
            'compute_price': 'percentage',
            'base': 'list_price',
            'price': 150,
            'percent_price': 10,
            'min_quantity': 2,
            'recurrence_id': cls.daily_recurrence.id,
            'pricelist_id': cls.rental_pricelist.id
        })

        cls.pricing_item_2 = cls.env['product.pricing'].create({
            'display_applied_on': '1_product',
            'product_tmpl_id': cls.conference_hall.product_tmpl_id.id,
            'compute_price': 'fixed',
            'price': 900,
            'fixed_price': 20000,
            'min_quantity': 2,
            'recurrence_id': cls.weekly_recurrence.id,
            'pricelist_id': cls.rental_pricelist.id
        })


    def test_compute_price_unit_all_pricing_rules(self):
        """ Test _compute_price_unit with different recurrence intervals """
        partner = self.env.ref('base.res_partner_12')
        now = fields.Datetime.now()

        order_daily = self.env['sale.order'].create({
            'partner_id': partner.id,
            'pricelist_id': self.rental_pricelist.id,
            'date_order': now,
            'rental_start_date': now,
            'rental_return_date': now + timedelta(days=2),
        })
        order_line_daily = self.env['sale.order.line'].create({
            'order_id': order_daily.id,
            'product_id': self.conference_hall.id,
            'start_date': now,
            'return_date': now + timedelta(days=2),
            'product_uom_qty': 1,
            'product_uom': self.conference_hall.uom_id.id,
        })
        expected_daily_price = self.conference_hall.list_price * 0.90 * 2
        self.assertEqual(order_line_daily.price_subtotal, expected_daily_price, "Daily pricing rule not applied correctly")

        order_weekly = self.env['sale.order'].create({
            'partner_id': partner.id,
            'pricelist_id': self.rental_pricelist.id,
            'date_order': now,
            'rental_start_date': now,
            'rental_return_date': now + timedelta(weeks=2),
        })
        order_line_weekly = self.env['sale.order.line'].create({
            'order_id': order_weekly.id,
            'product_id': self.conference_hall.id,
            'start_date': now,
            'return_date': now + timedelta(weeks=2),
            'product_uom_qty': 1,
            'product_uom': self.conference_hall.uom_id.id,
        })
        expected_weekly_price = self.pricing_item_2.fixed_price * 2
        self.assertEqual(order_line_weekly.price_unit, expected_weekly_price, "Weekly pricing rule not applied correctly")

