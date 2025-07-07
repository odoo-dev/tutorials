from odoo import Command, api, fields, models
from collections import defaultdict


class ModularTypeWizard(models.TransientModel):
    _name = "modular.type.wizard"
    _description = "Wizard to assign values to modular types for a Sale Order Line"

    line_ids = fields.One2many(
        comodel_name="modular.type.wizard.line",
        inverse_name="wizard_id",
        string="Modular Type Values",
        required=True,
    )
    sale_order_line_id = fields.Many2one(
        "sale.order.line", string="Sale Order Line", required=True
    )

    @api.model
    def default_get(self, field_ids):
        result = super().default_get(field_ids)
        if self.env.context.get(
            "active_model"
        ) == "sale.order.line" and self.env.context.get("active_id"):
            line = self.env["sale.order.line"].browse(self.env.context.get("active_id"))

            modular_type_ids = (
                line.product_id.product_tmpl_id.modular_type_ids
                if line.product_id
                else self.env["modular.type"]
            )

            existing_modular_type_vals = self.env[
                "sale.order.line.modular.type.value"
            ].search(
                [
                    ("sale_order_line_id", "=", line.id),
                    ("modular_type_id", "in", modular_type_ids.ids),
                ]
            )

            modular_type_dict = defaultdict(lambda: 0.0)
            for val in existing_modular_type_vals:
                modular_type_dict[val.modular_type_id.id] = val.value

            lines_data = []
            for mt in modular_type_ids:
                lines_data.append(
                    {"modular_type_id": mt.id, "value": modular_type_dict[mt.id]}
                )

            modular_type_wizard_lines = self.env["modular.type.wizard.line"].create(
                lines_data
            )

            result.update(
                {
                    "sale_order_line_id": line.id,
                    "line_ids": [Command.set(modular_type_wizard_lines.ids)],
                }
            )
        return result

    def save_values(self):
        self.ensure_one()
        self.sale_order_line_id.modular_type_line_ids.unlink()

        for line in self.line_ids:
            self.env["sale.order.line.modular.type.value"].create(
                {
                    "sale_order_line_id": self.sale_order_line_id.id,
                    "modular_type_id": line.modular_type_id.id,
                    "value": line.value,
                }
            )

        return {"type": "ir.actions.act_window_close"}
