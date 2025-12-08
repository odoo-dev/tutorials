from odoo import models, fields

class PosConfig(models.Model):
    _inherit = "pos.config"

    custom_text = fields.Char(string="Custom Congratulatory Text")