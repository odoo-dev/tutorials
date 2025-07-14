from odoo import Command
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.tests import tagged, Form


@tagged("post_install", "-at_install")
class EstateTestCase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(EstateTestCase, cls).setUpClass()
        cls.properties = cls.env["estate.property"].create(
            [
                {
                    "name": "Property 1",
                    "expected_price": 12000,
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": cls.env.ref("base.res_partner_2").id,
                                "price": 12000,
                            }
                        ),
                        Command.create(
                            {
                                "partner_id": cls.env.ref("base.res_partner_2").id,
                                "price": 12500,
                                "status": "accepted",
                            }
                        ),
                    ],
                },
                {
                    "name": "Property 2",
                    "expected_price": 13000,
                },
                {
                    "name": "Property 3",
                    "expected_price": 14000,
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": cls.env.ref("base.res_partner_2").id,
                                "price": 14500,
                            }
                        ),
                    ],
                },
            ]
        )

    def test_creation_offer_for_sold_property(self):
        """TEST CASE: Assert UserError when creating an offer for a sold property"""
        
        # Mark Property 1 as sold first
        self.properties[0].mark_as_sold()

        # Try to create an offer for Property 1, expecting UserError
        with self.assertRaises(UserError):
            self.properties[0].write(
                {
                    "offer_ids": [
                        Command.create(
                            {
                                "partner_id": self.env.ref("base.res_partner_2").id,
                                "price": 13000,
                            }
                        )
                    ]
                }
            )

        # Try to create an offer for Property 2, expecting no error
        self.properties[2].write(
            {
                "offer_ids": [
                    Command.create(
                        {
                            "partner_id": self.env.ref("base.res_partner_2").id,
                            "price": 15000,
                        }
                    )
                ]
            }
        )

        """
        Assert the following state for each property:

        Property 1: "sold"
        Property 2: "new"
        Property 3: "offer_received"
        """
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
        """TEST CASE: Assert UserError when selling a property without an accepted offer"""

        # Mark Property 1 as sold, expecting no error as there is an accepted offer
        self.properties[0].mark_as_sold()

        # Mark Property 2 as sold, expecting UserError as there is no accepted offer
        with self.assertRaises(UserError):
            self.properties[1].mark_as_sold()

        """
        Assert the following state for each property:

        Property 1: "sold"
        Property 2: "new"
        Property 3: "offer_received"
        """
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
        f = Form(self.env["estate.property"])
        f.name = "Property with garden"
        f.expected_price = 12000
        f.garden = True
        f.garden_area = 20
        f.garden_orientation = "east"
        f.save()

        f.garden = False
        self.assertEqual(f.garden_area, 0)
        self.assertEqual(f.garden_orientation, False)