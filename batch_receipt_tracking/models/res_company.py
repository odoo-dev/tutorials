# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    expiry_duration = fields.Integer(
        'Expiry Duration')
