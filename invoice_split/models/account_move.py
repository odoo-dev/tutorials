# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_split(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Invoice',
            'res_model': 'account.split.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('invoice_split.account_split_invoice_view_form').id,
            'target': 'new',
        }
