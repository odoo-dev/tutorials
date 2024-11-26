from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class EstatePropertyTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstatePropertyTestCase, cls).setUpClass()
        cls.property = cls.env['estate.property'].create({
                                                            'name': 'Test',
                                                            'expected_price': '1',
                                                            })

    def test_sell_no_offers(self):
        """Test that a property cannot be sold when there are no accepted offers: no offers at all."""
        self.property.offer_ids = []
        with self.assertRaises(UserError):
            self.property.action_set_sold()

    def test_sell_no_accepted_offers(self):
        """Test that a property cannot be sold when there are no accepted offers: some unaccepted offers are present."""
        offers = [
            self.env['estate.property.offer'].create({
                'property_id': self.property.id,
                'partner_id': 1,  # Trying to avoid having to create a new (irrelevant) res.partner record, appears to work
                'price': 1,
            }),
            self.env['estate.property.offer'].create({
                'property_id': self.property.id,
                'partner_id': 1,
                'price': 1,
                'state': 'refused'
            }),
        ]
        self.property.offer_ids = [offer.id for offer in offers]
        with self.assertRaises(UserError):
            self.property.action_set_sold()

    def test_sell_sets_sold(self):
        """Test that selling a property sets it to 'Sold'."""
        offers = [
            self.env['estate.property.offer'].create({
                'property_id': self.property.id,
                'partner_id': 1,
                'price': 1,
            }),
        ]
        self.property.offer_ids = [offer.id for offer in offers]
        offers[0].action_accept()
        self.property.action_set_sold()
        self.assertEqual(self.property.state, 'sold')