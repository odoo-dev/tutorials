from odoo import Command
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged, Form
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstateTestCase, cls).setUpClass()

        cls.properties = cls.env["estate.property"].create(
            [
                {
                    "name": "Big Villa",
                    "expected_price": 160,
                    "offer_ids": [
                        Command.create(
                            {
                                "validity": 14,
                                "price": 10000,
                                "partner_id": cls.env.ref("base.res_partner_1").id,
                            }
                        )
                    ],
                },
                {
                    "name": "Trailer home",
                    "expected_price": 100,
                },
                {
                    "name": "Ultra Big Villa",
                    "expected_price": 2,
                    "offer_ids": [
                        Command.create(
                            {
                                "validity": 14,
                                "price": 10000,
                                "partner_id": cls.env.ref("base.res_partner_1").id,
                            }
                        )
                    ],
                },
            ]
        )

    def test_create_offer_for_sold_property(self):
        self.properties[0].offer_ids[0].action_accept()
        self.properties[0].action_sold()

        with self.assertRaises(UserError):
            self.properties[0].write(
                {
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": self.env.ref("base.res_partner_1").id,
                                "price": 99999,
                            }
                        )
                    ]
                }
            )

        self.assertRecordValues(
            self.properties,
            [
                {"state": "sold"},
                {"state": "new"},
                {"state": "offer_received"},
            ],
        )

    def test_sell_property_without_accepting_offer(self):
        with self.assertRaises(ValidationError):
            self.properties[2].action_sold()

        self.assertRecordValues(
            self.properties,
            [
                {"state": "offer_received"},
                {"state": "new"},
                {"state": "offer_received"},
            ],
        )

    def test_is_garden_reset_when_unchecked(self):
        f = Form(self.env["estate.property"])

        f.name = "Test"
        f.expected_price = 1
        f.garden = True
        f.garden_area = 1
        f.garden_orientation = "east"
        f.save()

        f.garden = False
        self.assertEqual(f.garden_area, 0)
        self.assertFalse(f.garden_orientation)
