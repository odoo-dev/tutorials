from odoo import fields, models


class PosConfig(models.Model):

    _inherit = 'pos.config'

    simplified_receipt = fields.Boolean()
