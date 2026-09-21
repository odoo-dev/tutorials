from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "estate_property"

    def action_sell_property(self):
        return super().action_sell_property()
