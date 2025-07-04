from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def action_open_flask_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "XML File Wizard",
            "res_model": "modular.type.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_id": self.id,
            },
        }
