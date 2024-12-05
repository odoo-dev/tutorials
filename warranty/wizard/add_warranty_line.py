from odoo import api, fields, models
from datetime import date
from dateutil.relativedelta import relativedelta


class WarrantyLine(models.TransientModel):
    _name = "add.warranty.line"
    name = fields.Char(String="product")
    warranty_id = fields.Many2one("add.warranty.wizard")
    product_id = fields.Many2one("product.template")
    sale_order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    warranty_config_id = fields.Many2one("warranty.configuration", string="Year")
    end_date = fields.Date(compute="_compute_end_date", readonly=True)

    @api.depends("warranty_config_id")
    def _compute_end_date(self):
        for record in self:
            if record.warranty_config_id:
                today = date.today()
                record.end_date = today + relativedelta(
                    years=record.warranty_config_id.year
                )

            else:
                record.end_date = False
