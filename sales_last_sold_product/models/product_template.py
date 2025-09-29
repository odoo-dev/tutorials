from odoo import api, models
from datetime import datetime


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        partner_id = self.env.context.get("partner_id")
        if partner_id:
            recent_order_lines = self.env["account.move.line"].search(
                [("partner_id", "=", partner_id), ("product_id", "!=", None)],
                order="create_date desc",
            )
            recent_product_ids = recent_order_lines.mapped(
                "product_id.product_tmpl_id"
            ).ids

            ordered_products = self.browse(recent_product_ids)
            product_invoice_dates = {}

            for product_id in recent_product_ids:
                invoice_lines = self.env["account.move.line"].search(
                    [
                        ("partner_id", "=", partner_id),
                        ("product_id.product_tmpl_id", "=", product_id),
                    ],
                    order="create_date desc",
                    limit=1,
                )

                if invoice_lines:
                    invoice_date = invoice_lines[0].create_date
                    product_invoice_dates[product_id] = invoice_date

            result = []
            for product in ordered_products:
                invoice_date = product_invoice_dates.get(product.id)
                if invoice_date:
                    time_diff = datetime.now() - invoice_date
                    seconds = time_diff.total_seconds()
                    months = int(seconds // 2592000)
                    seconds = int(seconds % 2592000)
                    days = int(seconds // 86400)
                    seconds = int(seconds % 86400)
                    hours = int(seconds // 3600)
                    result.append(
                        (
                            product.id,
                            f"{product.display_name}      : {hours}h {days}d {months}mo",
                        )
                    )

            if len(recent_product_ids) >= limit:
                return result

            remaining_limit = limit - len(recent_product_ids)
            additional_products = self.search(
                [("id", "not in", recent_product_ids)], limit=remaining_limit
            )

            result.extend(
                map(
                    lambda product: (product.id, product.display_name),
                    additional_products,
                )
            )
            return result

        return super(ProductTemplate, self).name_search(name, args, operator, limit)
