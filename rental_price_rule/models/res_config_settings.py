from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    def set_values(self):
        super().set_values()
        products = self.env['product.template'].search([('is_pricelist_available', '!=', self.group_product_pricelist)])
        if products:
            products.write({'is_pricelist_available': self.group_product_pricelist})
