from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    congratulatory_text = fields.Char(default="Congratulations on your first purchase!!!!!!", optional=True)