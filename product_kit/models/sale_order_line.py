# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    show_kit_button = fields.Boolean(compute="_compute_show_kit_button")
    is_sub_product_line = fields.Boolean(string="Is Sub Product Line", default=False)
    parent_line_id = fields.Many2one("sale.order.line", string="Parent Kit Line")
    is_kit_component = fields.Boolean(default=False)
    wizard_price_unit = fields.Float("Wizard Price Unit", default=0.0)

    def _compute_show_kit_button(self):
        for line in self:
            is_kit = line.product_template_id.is_kit
            not_confirmed = line.order_id.state in ["draft", "sent"]
            line.show_kit_button = is_kit and not_confirmed

    def open_kit_popup(self):
        return {
            "name": "Configure Sub Products",
            "type": "ir.actions.act_window",
            "res_model": "kit.sub.product.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_line_id": self.id},
        }

    def unlink(self):
        for line in self:
            if not line.is_sub_product_line:
                sub_lines = self.search(
                    [
                        ("parent_line_id", "=", line.id),
                        ("is_sub_product_line", "=", True),
                    ]
                )
                if sub_lines:
                    sub_lines.unlink()
        return super().unlink()
