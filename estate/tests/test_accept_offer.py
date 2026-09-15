from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class EstateTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.property = cls.env["estate.property"].create(
            {
                "name": "test estate",
                "postcode": "6000",
                "description": "this is a test estate",
                "expected_price": "31415.92",
                "living_area": 100,
                "facades": 4,
            },
        )

        cls.partner = cls.env["res.partner"].create({"name": "bob"})

    def test_add_offer(self):
        self.assertRecordValues(
            self.property,
            [{"offer_ids": {}}],
        )

        offer_1 = self.env["estate.property.offer"].create(
            {
                "price": "28000",
                "partner_id": self.partner.id,
                "property_id": self.property.id,
            },
        )
        offer_2 = self.env["estate.property.offer"].create(
            {
                "price": "32000",
                "partner_id": self.partner.id,
                "property_id": self.property.id,
            },
        )

        self.assertRecordValues(
            self.property, [{"offer_ids": {offer_1.id, offer_2.id}}]
        )
        self.assertRecordValues(offer_2, [{"status": False}])

        with self.assertRaises(UserError):
            offer_1.action_accept_offer()

        offer_2.action_accept_offer()

        self.assertRecordValues(offer_2, [{"status": "accepted"}])
        self.assertRecordValues(offer_1, [{"status": "refused"}])

        self.assertRecordValues(
            self.property,
            [{"buyer_id": self.partner.id, "selling_price": offer_2.price}],
        )
