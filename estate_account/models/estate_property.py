from odoo import models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sell_property(self):
        for record in self:
            self.env["account.move"].create({
                "partner_id": record.buyer_id.id,
                "move_type": "out_invoice",
            })

        return super().action_sell_property()
