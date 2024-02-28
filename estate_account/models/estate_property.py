from odoo import models, Command


class estateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):

        super().action_sold()

        self.env["account.move"].sudo().create(
            {
                "partner_id": self.buyer_id.id,
                "move_type": "out_invoice",
                "line_ids": [
                    Command.create(
                        {
                            "name": self.name,
                            "quantity": 1,
                            "price_unit": 0.06 * self.selling_price,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Administrative Fees",
                            "quantity": 1,
                            "price_unit": 100,
                        }
                    ),
                ],
            }
        )

        # This is to create a project and a project task. Just for practice
        # project = self.env["project.project"].create(
        #     {
        #         "name": self.name,
        #         # "task_ids": [
        #         #     Command.create(
        #         #         {
        #         #             "name": self.name,
        #         #         }
        #         #     )
        #         # ]
        #     }
        # )

        # self.env["project.task"].create(
        #     {
        #         "name": self.name,
        #         "project_id": project.id
        #     }
        # )
        return True
