from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.types"
    _description = "Estate Property Types"

    name = fields.Char("Property Type", required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    sequence = fields.Integer(string="Sequence", default=1)
    offer_ids = fields.One2many("estate.property.offer", inverse_name="property_type_id", string="Offers")
    offers_count = fields.Integer(string="Offers Count", compute="_compute_offers_count")
    _order = "name asc"

    _check_type_name = models.Constraint(
        'UNIQUE(name)',
        'The type name should be unique.',
    )

    @api.depends("offer_ids")
    def _compute_offers_count(self):
        for record in self:
            print(f"Property Type: {record.name}")

            for offer in record.offer_ids:
                print("Offer object type:", type(offer))

                print(
                    f"Offer ID: {offer.id}, "
                    f"Property: {offer.property_id.title}, "
                    f"Price: {offer.price}"
                )

            record.offers_count = len(record.offer_ids)
