from odoo import Command, _, api, fields, models


class EstateProperty(models.Model):
    ## Private attributes ##
    _inherit = "estate.property"

    ## Fields declaration ##
    account_move_ids = fields.One2many("account.move", inverse_name="property_id")
    account_move_count = fields.Integer(compute="_compute_account_move_count")

    ## Compute methods ##
    @api.depends("account_move_ids")
    def _compute_account_move_count(self):
        for record in self:
            record.account_move_count = len(record.account_move_ids)

    ## Action methods ##
    def action_sold(self):
        res = super().action_sold()
        for record in self:
            self.env["account.move"].create(
                {
                    "partner_id": record.buyer_id.id,
                    "move_type": "out_invoice",
                    "property_id": record.id,
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": _("6% of selling price"),
                                "quantity": 1,
                                "price_unit": record.selling_price * 0.06,
                            },
                        ),
                        Command.create(
                            {
                                "name": _("Administrative fees"),
                                "quantity": 1,
                                "price_unit": 100.0,
                            },
                        ),
                    ],
                },
            )
        return res

    def action_view_invoices(self):
        self.ensure_one()
        return {
            "name": _("Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("property_id", "=", self.id)],
            "context": {"create": False},
        }
