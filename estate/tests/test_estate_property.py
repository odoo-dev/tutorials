from odoo import fields
from odoo.tests import TransactionCase


class TestEstateProperty(TransactionCase):
    def test_create_property(self):
        """
        Test if property is properly created
        Test if offer are properly created, comfirmed and refused
        """
        name = "test_name"
        description = "test_description"
        postcode = "1234"
        expected_price = 10000.00
        bedrooms = 2
        living_area = 10
        facades = 4
        has_garage = True
        has_garden = True
        garden_area = 5
        garden_orientation = "north"
        price_offer1 = 9000.00
        status_offer1 = "refused"
        price_offer2 = 10000.00
        status_offer2 = "accepted"

        record = self.env["estate.property"].create(
            {
                "name": name,
                "description": description,
                "postcode": postcode,
                "expected_price": expected_price,
                "bedrooms": bedrooms,
                "living_area": living_area,
                "facades": facades,
                "has_garage": has_garage,
                "has_garden": has_garden,
                "garden_area": garden_area,
                "garden_orientation": garden_orientation,
            },
        )

        # Check basic Fields
        self.assertRecordValues(
            record,
            [
                {
                    "name": name,
                    "description": description,
                    "postcode": postcode,
                    "expected_price": expected_price,
                    "bedrooms": bedrooms,
                    "living_area": living_area,
                    "facades": facades,
                    "has_garage": has_garage,
                    "has_garden": has_garden,
                    "garden_area": garden_area,
                    "garden_orientation": garden_orientation,
                },
            ],
        )

        # Check Default and Computed Fields
        self.assertEqual(record.total_area, living_area + garden_area)
        self.assertEqual(
            record.date_availability,
            fields.Date.add(fields.Date.today(), months=3),
        )
        self.assertEqual(record.selling_price, 0)
        self.assertEqual(record.best_price, 0)
        self.assertEqual(record.active, True)

        partner_id = self.env["res.partner"].create({"name": "Test Partner"}).id
        property_id = record.id

        offer1_record = self.env["estate.property.offer"].create(
            {
                "partner_id": partner_id,
                "property_id": property_id,
                "price": price_offer1,
            },
        )

        offer2_record = self.env["estate.property.offer"].create(
            {
                "partner_id": partner_id,
                "property_id": property_id,
                "price": price_offer2,
            },
        )

        self.assertEqual(len(record.offer_ids), 2)
        self.assertIn(offer1_record, record.offer_ids)
        self.assertIn(offer2_record, record.offer_ids)

        # Check Compute Field of Property
        self.assertEqual(record.best_price, price_offer2)

        # Confirm Offer
        offer2_record.action_confirm_offer()

        self.assertEqual(offer2_record.status, status_offer2)

        # Refuse Offer
        offer1_record.action_refuse_offer()

        self.assertEqual(offer1_record.status, status_offer1)

        # Check Compute Field of Property
        self.assertEqual(record.selling_price, price_offer2)
