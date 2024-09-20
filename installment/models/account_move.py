from datetime import timedelta
from odoo import Command, models, fields, api


class accountMove(models.Model):
    _inherit = "account.move"

    applied_penalty = fields.Boolean(string="Applied Penalty", default=False)

    @api.model
    def cron_recurring_create_invoice(self):

        today = fields.Date.today()
        delay_penalty_process = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("installment.delay_penalty_process")
        )

        invoices = self.env["account.move"].search(
            [
                ("state", "=", "posted"),
                ("payment_state", "=", "not_paid"),
                ("move_type", "=", "out_invoice"),
                ("applied_penalty", "=", False),
            ]
        )
        for invoice in invoices:

            for line in invoice.line_ids:
                if (
                    line.product_id.id
                    == self.env.ref("installment.product_product_installment").id
                ):
                    due_date = invoice.invoice_date_due

                    penalty_start_date = due_date + timedelta(
                        days=delay_penalty_process
                    )

                    if today >= penalty_start_date:
                        penalty_amount = self.calculate_penalty_amount(invoice)

                        invoice_vals = {
                            "partner_id": invoice.partner_id.id,
                            "move_type": "out_invoice",
                            "line_ids": [
                                Command.create(
                                    {
                                        "product_id": self.env.ref(
                                            "installment.product_product_installment"
                                        ).id,
                                        "name": "Installment",
                                        "price_unit": invoice.amount_total,
                                        "tax_ids": None,
                                    }
                                ),
                                Command.create(
                                    {
                                        "product_id": self.env.ref(
                                            "installment.product_product_penalty"
                                        ).id,
                                        "name": "Penalty Charge",
                                        "price_unit": penalty_amount,
                                        "tax_ids": None,
                                    }
                                ),
                            ],
                        }
                        new_invoice = (
                            self.env["account.move"].sudo().create(invoice_vals)
                        )
                        new_invoice.action_post()
                        invoice.write({"applied_penalty": True})

    def calculate_penalty_amount(self, invoice):

        down_penalty_percentage = float(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("installment.down_penalty_percentage")
        )
        penalty_amount = (invoice.amount_total * down_penalty_percentage) / 100
        return penalty_amount
