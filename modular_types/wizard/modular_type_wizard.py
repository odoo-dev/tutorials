from odoo import models, fields, api


class ModularTypeWizard(models.TransientModel):
    _name = "modular.type.wizard"

    line_ids = fields.One2many("modular.type.wizard.line", "wizard_id")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_order_line_id = self.env.context.get("default_sale_order_id")
        sale_order_line = self.env["sale.order.line"].browse(sale_order_line_id)
        res["sale_order_line_id"] = sale_order_line_id
        existing_values = {
            v.modular_type_id.id: v.value
            for v in self.env["sale.order.line.modular.type.value"].search(
                [("sale_order_line_id", "=", sale_order_line.id)]
            )
        }
        lines = []
        for modular_type in sale_order_line.product_id.modular_type_ids:
            lines.append(
                (
                    0,
                    0,
                    {
                        "modular_type_id": modular_type.id,
                        "value": existing_values.get(modular_type.id, 0),
                    },
                )
            )
        res["line_ids"] = lines
        return res
