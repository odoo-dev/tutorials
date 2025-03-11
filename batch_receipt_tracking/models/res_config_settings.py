# -*- coding: utf-8 -*-

from odoo import api, models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expiry_duration = fields.Selection(
        [(str(i), f'{i} month{"" if i == 1 else "s"}') for i in range(1, 13)],
        string='Expiry Duration'
    )
    user_ids = fields.Many2many(
        'res.users', string='Validated By',
        default=lambda self: [(6, 0, [self.env.user.id])], copy=False
    )

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param(
            'batch_receipt_tracking.expiry_duration', self.expiry_duration)
        self.env['ir.config_parameter'].set_param(
            'batch_receipt_tracking.user_ids', ','.join(map(str, self.user_ids.ids)))

    @api.model
    def get_values(self):
        res = super().get_values()
        param_env = self.env['ir.config_parameter']
        user_ids = param_env.get_param('batch_receipt_tracking.user_ids', '')
        res.update(
            expiry_duration=param_env.get_param(
                'batch_receipt_tracking.expiry_duration', '0'),
            user_ids=[(6, 0, list(map(int, user_ids.split(','))))
                      ] if user_ids else [(6, 0, [])]
        )
        return res
