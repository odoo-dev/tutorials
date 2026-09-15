from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEstateProperty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.buyer_1 = cls.env["res.partner"].create({"name": "Buyer 1"})
        cls.buyer_2 = cls.env["res.partner"].create({"name": "Buyer 2"})

    def test_accept_offer(self):
        estate = self.env["estate.property"].create(
            {
                "name": "Test estate",
                "expected_price": 100000,
            }
        )

        offer_1 = self.env["estate.property.offer"].create(
            {
                "price": 80000,
                "partner_id": self.buyer_1.id,
                "property_id": estate.id,
            }
        )
        offer_2 = self.env["estate.property.offer"].create(
            {
                "price": 95000,
                "partner_id": self.buyer_2.id,
                "property_id": estate.id,
            }
        )

        offer_1.action_refuse()
        offer_2.action_confirm()

        self.assertEqual(offer_1.status, "refused")
        self.assertEqual(offer_2.status, "accepted")
        self.assertEqual(estate.state, "sold")
        self.assertEqual(estate.selling_price, 95000)
        self.assertEqual(estate.buyer_id, self.buyer_2)
