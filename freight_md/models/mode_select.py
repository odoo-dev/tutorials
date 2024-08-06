from odoo import models, fields


class ModeSelect(models.Model):
    _name = 'mode.select'
    _description = 'mode'

    name = fields.Char(string='Name', required=True)
