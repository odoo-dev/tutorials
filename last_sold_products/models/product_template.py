from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    last_invoice_time_diff = fields.Char(string="Last Invoice Time", compute="_compute_last_invoice_time_diff")

    def _compute_last_invoice_time_diff(self):
        for record in self:
            record.last_invoice_time_diff = False

        partner_id = self.env.context.get("partner_id")

        if not partner_id:
            return

        last_ordered_products = self._get_last_sold_data(partner_id)

        for record in self:
            last_date_info = last_ordered_products.get(record.id)
            if last_date_info:
                last_date, create_date = last_date_info
                record.last_invoice_time_diff = self._get_time_ago_string(last_date, create_date)

    def _get_last_sold_data(self, partner_id):
        
        invoice_lines = self.env["account.move.line"].search(
            [
                ("move_id.partner_id", "=", partner_id),
                ("move_id.state", "=", "posted"),
                ("move_id.move_type", "in", ["out_invoice","out_receipt","out_refund"]),
                ("product_id.product_tmpl_id", "!=", False),
            ], order="invoice_date desc, move_id.id desc, id asc")

        last_sold_data = {}
        for line in invoice_lines:
            product_tmpl_id = line.product_id.product_tmpl_id.id
            if product_tmpl_id not in last_sold_data:
                invoice_date = line.move_id.invoice_date
                create_date = line.move_id.create_date
                if invoice_date:
                    last_sold_data[product_tmpl_id] = (invoice_date, create_date)
        return last_sold_data

    def _get_time_ago_string(self, last_date, create_date=None):
        if not last_date:
            return ""

        now = fields.Datetime.now()
        diff = now.date() - last_date

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
        context_partner_id = self._context.get("partner_id")
        last_sold_data = self._get_last_sold_data(context_partner_id)

        if not context_partner_id or not last_sold_data:
            return super().name_search(name, args, operator, limit)

        last_sold_template_ids = list(last_sold_data.keys())

        last_sold_products = self.search([("id", "in", last_sold_template_ids), ("name", operator, name)] + args,
            limit=limit)

        other_products = self.search([("id", "not in", last_sold_template_ids), ("name", operator, name)] + args,
            limit=limit - len(last_sold_products))

        sorted_last_sold = sorted(last_sold_products, key=lambda p: last_sold_template_ids.index(p.id))

        return [(product.id, f"{product.display_name}|||{product.last_invoice_time_diff or ''}")
            for product in sorted_last_sold] + [(product.id, product.display_name) for product in other_products]
    