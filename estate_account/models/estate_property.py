from typing import override

from odoo import models, fields


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sell(self):
        print("OVERRIDE")
        return super().action_sell()
