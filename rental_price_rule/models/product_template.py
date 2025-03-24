from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    is_pricelist_available = fields.Boolean(string="Pricelist Available")
    pricelist_item_ids = fields.One2many('product.pricelist.item','product_tmpl_id',string='Pricelist Rules')
