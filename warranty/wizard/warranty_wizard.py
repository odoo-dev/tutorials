from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import api, Command, fields, models


class WarrantyWizard(models.TransientModel):
    _name = "warranty.wizard"
    _description = "Warranty Management Wizard"

    warranty_line_ids = fields.One2many(
        "warranty.wizard.line", "wizard_id", string="Warranty Lines"
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        sale_order = self.env["sale.order"].browse(self.env.context.get("active_id"))

        lines = []
        for line in sale_order.order_line:
            if line.product_id.is_warranty_available:
                # Check if warranty is available
                lines.append(
                    (
                        0,
                        0,
                        {"product_id": line.id, "name": line.name},
                    )
                )
        res["warranty_line_ids"] = lines
        return res

    def apply_warranties(self):
        active_id = self.env.context.get("active_id")
        sale_order = self.env["sale.order"].browse(active_id)

        for line in self.warranty_line_ids:

            if line.year:
                for record in sale_order.order_line:
                    if record.id == line.product_id.id:
                        price = (record.price_subtotal * line.year.percentage) / 100
                        sale_order.order_line = [
                            Command.create(
                                {
                                    "name": f"Extended Warranty ({line.year.name})",
                                    "order_id": sale_order.id,
                                    "product_id": line.year.product_id.id,
                                    "product_uom": 1,
                                    "product_uom_qty": 1,
                                    "price_unit": price,
                                    "tax_id": None,
                                    "warranty_product_line_id": record.id,
                                }
                            )
                        ]


class WarrantyWizardLine(models.TransientModel):
    _name = "warranty.wizard.line"
    _description = "Warranty Wizard Line"

    name = fields.Char("Product")
    year = fields.Many2one("add.warranty")
    end_date = fields.Date(string="End Date")
    # product_id = fields.Many2one("product.product", string="Product")
    product_id = fields.Many2one("sale.order.line", string="Product")
    wizard_id = fields.Many2one("warranty.wizard", string="Wizard")

    @api.onchange("year")
    def _onchange_year(self):
        if self.year:
            self.end_date = date.today() + relativedelta(years=self.year.period)
        else:
            self.end_date = False
