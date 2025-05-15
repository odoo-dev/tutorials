from odoo import fields, models


class PosConfig(models.Model):
    _name = 'pos.config'
    _inherit = ['pos.config']

    congratulatory_text = fields.Char(string="Congratulatory text on receipt", default="Thank you!")
