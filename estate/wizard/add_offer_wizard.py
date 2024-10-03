from odoo import fields, models


class addofferwizardproperties(models.TransientModel):
    _name = "add.offers.wizard.properties"
    _description = "wizard for adding offers to properties"

    price = fields.Float(required=True)
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], string="Status", copy=False
    )
    Buyer_id = fields.Many2one("res.partner", string="Buyer", required=True)

    def add_offer_wizard_properties(self):
        active_ids = self.env.context.get("active_ids", [])
        properties = self.env["estate.property"].browse(active_ids)
        for record in properties:
            self.env["estate.property.offer"].create(
                {
                    "property_id": record.id,
                    "price": self.price,
                    "status": self.status,
                    "partner_id": self.Buyer_id.id,
                }
            )