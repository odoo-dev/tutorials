from odoo.tests import TransactionCase


class TestEstateCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestEstateCommon, cls).setUpClass()

        # ==== Partners ====
        cls.partner_a = cls.env['res.partner'].create({
            'name': 'partner_a'
        })
        cls.partner_b = cls.env['res.partner'].create({
            'name': 'partner_b'
        })

        # ==== Properties ====
        cls.property_1 = cls.env['estate.property'].create({
            'name': 'property1',
            'expected_price': 1000,
            'state': 'offer_received'
        })
        cls.property_2 = cls.env['estate.property'].create({
            'name': 'property2',
            'expected_price': 2000,
            'state': 'offer_received'
        })

        # ==== Offers ====
        cls.offer_1 = cls.env['estate.property.offer'].create({
            'partner_id': cls.partner_b.id,
            'property_id': cls.property_1.id,
            'price': 1200000
        })
        cls.offer_2 = cls.env['estate.property.offer'].create({
            'partner_id': cls.partner_a.id,
            'property_id': cls.property_2.id,
            'price': 2300000
        })
