# -*- coding: utf-8 -*-

from odoo import models, fields, Command

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_property_sold(self):
        self.ensure_one()
        val = {
            "partner_id" : self.buyer_id.id,
            "move_type" : "out_invoice",
            "invoice_line_ids" : [
                Command.create({"name": self.name, "quantity": 1, "price_unit": self.selling_price*0.06}),
                Command.create({"name": "administrative fees", "quantity": 1, "price_unit": 100.00})
            ]
        }

        self.env["account.move"].sudo().create(val)
        return super().action_property_sold()