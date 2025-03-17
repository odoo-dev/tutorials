from odoo import _, fields, models


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    sale_order_id = fields.Many2one('sale.order', domain="[('order_line.product_id','=',product_id)]") 
    purchase_order_id = fields.Many2one('purchase.order', domain="[('order_line.product_id','=',product_id)]") 
    