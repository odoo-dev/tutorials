from odoo import models, fields


class OfferEntryWizard(models.TransientModel):
    _name = "offer.entry.wizard"
    _description = "Offer entry wizard"

    validity = fields.Integer(string="Validity (days)", default=7)
    price = fields.Float(string="Price")
    partner_id = fields.Many2one("res.partner", string="Partner")

    def offer_save(self):
        selected_props = self.env.context.get("active_ids", [])
        properties = self.env["estate.property"].browse(selected_props)
        for record in properties:
            self.env["estate.property.offer"].create(
                {
                    "property_id": record.id,
                    "price": self.price,
                    "validity": self.validity,
                    "partner_id": self.partner_id.id,
                }
            )
        return {"type": "ir.actions.act_window_close"}
