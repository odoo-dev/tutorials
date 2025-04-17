# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    deposit_product = fields.Many2one('product.product', string='Deposit')

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('rental_deposit.deposit_product_id', self.deposit_product.id)

    @api.model
    def get_values(self):
        res = super().get_values()
        product_id = int(self.env['ir.config_parameter'].sudo().get_param('rental_deposit.deposit_product_id', default=0))
        res.update(deposit_product=self.env['product.product'].browse(product_id))
        return res