# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    expiry_duration = fields.Selection(
        [(str(i), '{} month{}'.format(i, 's' if i > 1 else ''))
         for i in range(1, 13)],
        string='Expiry Duration', )

    user_ids = fields.Many2many(
        'res.users', string='Validated By',
        default=lambda self: [(6, 0, [self.env.user.id])], copy=False
    )
