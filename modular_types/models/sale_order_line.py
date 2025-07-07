from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    modular_type_line_ids = fields.One2many(
        "sale.order.line.modular.type.value",
        "sale_order_line_id",
    )

    def action_open_flask_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "XML File Wizard",
            "res_model": "modular.type.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_line_id": self.id,
            },
        }

    def _prepare_production_vals(self, bom):
        res = super()._prepare_production_vals(bom)
        res["sale_order_line_id"] = self.id
        return res
