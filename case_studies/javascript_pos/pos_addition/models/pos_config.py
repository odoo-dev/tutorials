from odoo import fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    congratulatory_text = fields.Char(default="This is a sample congratulatory text that is supposed to be printed at the end of the PoS receipt")