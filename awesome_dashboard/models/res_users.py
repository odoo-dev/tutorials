from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    dashboard_hidden_items = fields.Char(default="[]")
