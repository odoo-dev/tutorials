from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from odoo.addons.estate.tests.common import TestEstateCommon


@tagged('post_install', '-at_install')
class TestEstatePropertyOffer(TestEstateCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_action_set_sold(self):
        # Test for failed: state cancelled
        cancelled_property = self.env['estate.property'].create({
            'name': 'property3',
            'expected_price': 2000,
            'state': 'cancelled'
        })
        with self.assertRaises(UserError):
            cancelled_property.action_set_sold()

        # Test for failed: state other than accepted
        with self.assertRaises(UserError):
            offer_received_property = self.property_1
            offer_received_property.action_set_sold()

        # Test for success
        offer_accepted_property = self.property_2
        offer_accepted_property.write({
            'state': 'offer_accepted',
            'buyer_id': self.partner_a.id,
            'best_price': 2300000
        })
        self.offer_2.write({
            'status': 'accepted'
        })
        offer_accepted_property.action_set_sold()
        self.assertEqual(offer_accepted_property.state, 'sold')

    def test_garden_visible(self):
        property_form = Form(self.env['estate.property'])

        # Garden checked: garden_area and garden_orientation with default value
        property_form.garden = True
        self.assertEqual(property_form.garden_area, 10)
        self.assertEqual(property_form.garden_orientation, 'north')

        # Garden unchecked: garden_area and garden_orientation empty
        property_form.garden = False
        self.assertFalse(property_form.garden_area)
        self.assertFalse(property_form.garden_orientation)
