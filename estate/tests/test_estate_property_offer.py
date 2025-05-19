from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.estate.tests.common import TestEstateCommon


@tagged('post_install', '-at_install')
class TestEstatePropertyOffer(TestEstateCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create(self):
        # Test for failed: price lower
        with self.assertRaises(UserError):
            self.env['estate.property.offer'].create({
                'partner_id': self.partner_a.id,
                'property_id': self.property_1.id,
                'price': 10
            })

        # Test for failed: state sold
        sold_property = self.env['estate.property'].create({
            'name': 'property_sold',
            'expected_price': 2000,
            'state': 'sold'
        })
        with self.assertRaises(ValidationError):
            self.env['estate.property.offer'].create({
                'partner_id': self.partner_a.id,
                'property_id': sold_property.id,
                'price': 3000
            })

        # Test for Success
        self.env['estate.property.offer'].create({
            'partner_id': self.partner_b.id,
            'property_id': self.property_2.id,
            'price': 2500000
        })
