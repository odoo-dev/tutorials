from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    last_invoice_time_diff = fields.Char(string="Last Invoice Time", compute="_compute_last_invoice_time_diff")

    def _compute_last_invoice_time_diff(self):
        for record in self:
            record.last_invoice_time_diff = False

        if self.env.context.get("active_model") == "sale.order.line":
            order = self.env["sale.order"].browse(self.env.context.get("order_id"))
            partner_id = order.partner_id.id
            order_type = "sale"
        elif self.env.context.get("active_model") == "purchase.order.line":
            order = self.env["purchase.order"].browse(self.env.context.get("order_id"))
            partner_id = order.partner_id.id
            order_type = "purchase"     
        elif self.env.context.get("order_type") == "invoice":
            partner_id = self.env.context.get("default_partner_id")
            order_type = "invoice"        
        else:
            partner_id = self.env.context.get("partner_id")
            order_type = self.env.context.get("order_type")

        if not partner_id:
            return

        last_ordered_products = {}
        if order_type == "sale" or order_type == "invoice":
            last_ordered_products = self._get_last_sold_data(partner_id, ["out_invoice","out_receipt","out_refund"])
        elif order_type == "purchase":
            last_ordered_products = self._get_last_sold_data(partner_id, ["in_invoice", "in_receipt", "in_refund"])
        else:
            return

        for record in self:
            last_date_info = last_ordered_products.get(record.id)
            if last_date_info:
                record.last_invoice_time_diff = self._get_time_ago_string(last_date_info)

    def _get_last_sold_data(self, partner_id, move_type):
        if not partner_id:
            return {}

        invoice_lines = self.env["account.move.line"].search(
            [
                ("move_id.state", "=", "posted"),
                ("move_id.move_type", "in", move_type),
                ("product_id", "!=", False),
                ("move_id.partner_id", "=", partner_id),
            ], order="invoice_date desc, move_id.id desc, id asc")

        last_sold_data = {}
        for line in invoice_lines:
            product_id = line.product_id.id
            if product_id not in last_sold_data:
                invoice_date = line.move_id.invoice_date
                create_date = line.move_id.create_date
                if invoice_date:
                    last_sold_data[product_id] = {"invoice_date": invoice_date, "create_date": create_date}
        return last_sold_data

    def _get_time_ago_string(self, last_date_info):
        if not last_date_info:
            return ""

        now = fields.Datetime.now()
        invoice_date = last_date_info.get("invoice_date")
        create_date = last_date_info.get("create_date")

        if not invoice_date:
            return ""

        diff = now.date() - invoice_date

        if diff.days > 365:
            return f"{diff.days // 365}y"
        elif diff.days > 30:
            return f"{diff.days // 30}mo"
        elif diff.days > 0:
            return f"{diff.days}d"
        else:
            if create_date:
                time_diff = now - create_date
                hours = time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                if hours > 0:
                    return f"{hours}h"
                elif minutes > 0:
                    return f"{minutes}m"
            return "just now"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        invoice_partner_id = self._context.get("default_partner_id")
        purchase_partner_id = self._context.get("partner_id")
        last_invoiced_data = self._get_last_sold_data(invoice_partner_id, ["out_invoice","out_receipt","out_refund"])
        last_purchased_data = self._get_last_sold_data(purchase_partner_id, ["in_invoice", "in_receipt", "in_refund"])
        
        last_invoiced_product_ids = list(last_invoiced_data.keys())
        last_purchased_product_ids = list(last_purchased_data.keys())

        combined_product_ids = list(set(last_invoiced_product_ids + last_purchased_product_ids))
        if not combined_product_ids:
            return super().name_search(name, args, operator, limit)
            
        prioritized_products = self.search([("id", "in", combined_product_ids), ("name", operator, name)] + args,
            limit=limit)
        other_products = self.search([("id", "not in", combined_product_ids), ("name", operator, name)] + args,
            limit=limit - len(prioritized_products))

        def get_product_index(product):
            if product.id in last_invoiced_product_ids:
                return last_invoiced_product_ids.index(product.id)
            elif product.id in last_purchased_product_ids:
                return last_purchased_product_ids.index(product.id)
            return None

        sorted_prioritized = sorted(prioritized_products, key=get_product_index)

        return [(product.id, f"{product.display_name}|||{product.last_invoice_time_diff or ''}")
            for product in sorted_prioritized] + [(product.id, product.display_name) for product in other_products]
