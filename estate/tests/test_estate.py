from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged, Form
from odoo import Command


@tagged('post_install', '-at_install')
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstateTestCase, cls).setUpClass()

        cls.sold_property = cls.env['estate.property'].create({
            'name': 'Sold House',
            'expected_price': 100000,
            'state': 'sold',
        })

        cls.no_offer_property = cls.env['estate.property'].create({
            'name': 'No Offer House',
            'expected_price': 200000,
        })

        cls.has_offer_property = cls.env['estate.property'].create({
            'name': 'Has Offer House',
            'expected_price': 300000,
            'offer_ids': [
                Command.create({
                    'price': 250000,
                    'validity': 7,
                    'partner_id': cls.env['res.partner'].create({'name': 'Buyer 1'}).id,
                    'status': 'accepted'
                }),
                Command.create({
                    'price': 260000,
                    'validity': 15,
                    'partner_id': cls.env['res.partner'].create({'name': 'Buyer 2'}).id,
                    'status': 'refused'
                }),
            ],
        })

    def test_create_offer_on_sold_property(self):
        """Test that creating an offer on a sold property raises a UserError."""
        with self.assertRaises(UserError):
            self.env['estate.property.offer'].create({
                'price': 900,
                'property_id': self.sold_property.id,
            })

    def test_action_sold_without_accepted_offer(self):
        """Test that selling a property without an accepted offer raises a UserError."""
        with self.assertRaises(UserError):
            self.no_offer_property.action_sold()

    def test_action_sold_property_state(self):
        """Test that selling a property with an accepted offer changes its state to 'sold'."""
        self.has_offer_property.action_sold()
        self.assertEqual(self.has_offer_property.state, 'sold')

    def test_garden_reset_form(self):
        """Test that unchecking the garden field resets garden_area and garden_orientation."""
        f = Form(self.env['estate.property'])

        f.name = 'Test Property'
        f.expected_price = 100000
        f.garden = True
        f.garden_area = 50
        f.garden_orientation = 'north'
        f.save()

        f.garden = False
        self.assertFalse(f.garden_area)
        self.assertFalse(f.garden_orientation)
