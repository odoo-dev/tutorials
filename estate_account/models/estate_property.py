from odoo import api, models, Command, fields


class EstateProperty(models.Model):
    _inherit = "estate.property"

    account_move_ids = fields.One2many("account.move", inverse_name="property_id")
    account_move_count = fields.Integer(compute="_compute_account_move_count")

    @api.depends("account_move_ids")
    def _compute_account_move_count(self):
        for record in self:
            record.account_move_count = len(record.account_move_ids)

    def action_sold(self):
        for record in self:
            self.env["account.move"].create(
                {
                    "partner_id": record.buyer_id.id,
                    "move_type": "out_invoice",
                    "property_id": record.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "6% of selling price",
                                "quantity": 1,
                                "price_unit": record.selling_price * 0.06,
                            },
                        ),
                        Command.create(
                            {
                                "name": "Administrative fees",
                                "quantity": 1,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                },
            )
        return super().action_sold()

    def action_view_invoices(self):
        self.ensure_one()
        return {
            "name": "Invoices",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("property_id", "=", self.id)],
            "context": {"create": False},
        }
