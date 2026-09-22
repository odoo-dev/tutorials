from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.properties = cls.env['estate.property'].create({
            'name': 'test_property',
            'expected_price': 50000,
        })

        cls.offers = cls.env['estate.property.offer'].create({
            'partner_id': 1,
            'property_id': cls.properties[0].id,
        })

    def test_creation_area(self):
        """Test that the total_area is computed as it should"""
        self.properties.living_area = 20
        self.properties.garden_area = 10
        self.assertRecordValues(self.properties, [
            {'name': 'test_property', 'total_area': 30}
        ])

    def test_action_sell(self):
        """Test that everything behaves as it should when selling property"""
        self.properties.action_mark_as_sold()
        self.assertRecordValues(self.properties, [
            {'name': 'test_property', 'state': 'sold'},
        ])
