# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    expiry_duration = fields.Integer(
        'Expiry Duration', related="company_id.expiry_duration", readonly=False,)
