from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    book_price = fields.Float(
        string="Book Price",
        compute="_compute_book_price",
        store=True,
    )

    @api.depends("product_id", "product_uom_qty", "order_id.pricelist_id")
    def _compute_book_price(self):
        for record in self:
            if record.product_id and record.order_id.pricelist_id:
                product = record.product_id
                pricelist = record.order_id.pricelist_id
                qty = record.product_uom_qty or 1
                partner = record.order_id.partner_id
                price = product.with_context(
                    pricelist=pricelist.id,
                    quantity=qty,
                    partner_id=partner.id,
                )._get_contextual_price()

                record.book_price = price or 0.0
            else:
                record.book_price = 0.0


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    book_price = fields.Float(
        string="Book Price",
        compute="_compute_book_price_invoice",
        store=True,
    )

    @api.depends("product_id", "quantity", "move_id.partner_id")
    def _compute_book_price_invoice(self):
        for record in self:
            if record.product_id and record.move_id.move_type == "out_invoice":
                product = record.product_id
                qty = record.quantity or 1
                partner = record.move_id.partner_id
                pricelist = False
                if record.sale_line_ids:
                    pricelist = record.sale_line_ids[0].order_id.pricelist_id

                if pricelist:
                    price = product.with_context(
                        pricelist=pricelist.id,
                        quantity=qty,
                        partner_id=partner.id,
                    )._get_contextual_price()

                    record.book_price = price or 0.0
                else:
                    record.book_price = 0.0
            else:
                record.book_price = 0.0
