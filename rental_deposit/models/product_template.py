# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    require_deposit = fields.Boolean(string='Required Deposit')
    deposit_amount = fields.Float(string='Deposit Amount', default=0.0)

    @api.onchange('require_deposit')
    def _onchange_require_deposit(self):
        if not self.require_deposit:
            self.deposit_amount = 0.0