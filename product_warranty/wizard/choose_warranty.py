from odoo import api, fields, models


class ChooseWarranty(models.TransientModel):
    _name = 'choose.warranty'
    _description = "Add warranty"

    order_id = fields.Many2one('sale.order', string="Order", required=True)
    product_id = fields.Many2one(
        'product.template',
        string="Product",
        required=True,
        domain=[('is_warranty', '=', True)],
    )
    warranty_id = fields.Many2one(
        'product.warranty.config',
        string="Select warranty",
        required=True,
        domain=[('product_tmpl_id', '=', product_id)],
    )

    def action_add_warranty(self):
        for wizard in self:
            sale_order = wizard.order_id
            warranty_product = wizard.warranty_id.product_tmpl_id
            price_percentage = wizard.warranty_id.percentage

            if warranty_product:
                sale_order.order_line.create({
                    'order_id': sale_order.id,
                    'product_id': warranty_product.id,
                    'name': f"{warranty_product.name} - {wizard.warranty_id.name}",
                    'price_unit': (sale_order.amount_total * price_percentage) / 100,
                    'product_uom_qty': 1,
                })
