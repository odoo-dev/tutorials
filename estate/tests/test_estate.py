from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged, Form


@tagged("post_install", "-at_install")
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstateTestCase, cls).setUpClass()
        cls.properties = cls.env["estate_property"].create(
            [
                {
                    "name": "Test Apartment",
                    "expected_price": 1200,
                    "garden_area": 5,
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": cls.env.ref("base.res_partner_12").id,
                                "price": 1000,
                            }
                        ),
                        Command.create(
                            {
                                "partner_id": cls.env.ref("base.res_partner_2").id,
                                "price": 1100,
                                "status": "accepted",
                            }
                        ),
                    ],
                },
                {"name": "Test Villa", "expected_price": 3000, "garden_area": 10},
                {
                    "name": "Test Office",
                    "expected_price": 5000,
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": cls.env.ref("base.res_partner_12").id,
                                "price": 4900,
                            }
                        ),
                    ],
                },
            ]
        )

    def test_creation_offer_for_sold_property(self):
        """Test if the code prohibits the creation of offer for sold property"""
        self.properties[0].action_set_property_sold()

        with self.assertRaises(UserError):
            self.properties[0].write(
                {
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": self.env.ref("base.res_partner_12").id,
                                "price": 9999999,
                            }
                        )
                    ]
                }
            )

        self.properties[2].write(
            {
                "offer_ids": [
                    Command.create(
                        {
                            "partner_id": self.env.ref("base.res_partner_12").id,
                            "price": 9999999,
                        }
                    )
                ]
            }
        )

        self.assertRecordValues(
            self.properties,
            [
                {
                    "state": "sold"
                },
                {
                    "state": "new"
                },
                {
                    "state": "offer_received"
                },
            ],
        )

    def test_sell_property_without_accepted_offer(self):
        """Test if code prevents selling properties with no accepted offer"""
        self.properties[0].action_set_property_sold()

        with self.assertRaises(UserError):
            self.properties[1].action_set_property_sold()

        self.assertRecordValues(
            self.properties,
            [
                {
                    "state": "sold"
                },
                {
                    "state": "new"
                },
                {
                    "state": "offer_received"
                },
            ]
        )

    def test_is_garden_reset_on_uncheck(self):
        f = Form(self.env["estate_property"])
        f.name = "Test Basement"
        f.expected_price = 12000
        f.garden = True
        f.garden_area = 20
        f.garden_orientation = "east"
        f.save()
        f.garden = False
        self.assertEqual(f.garden_area, 0)
        self.assertEqual(f.garden_orientation, False)