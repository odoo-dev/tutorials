from odoo import fields, models

class PosConfig(models.Model):
    _inherit = "pos.config"

    is_congratulatory_message = fields.Boolean(string="Enable Congratulatory Message")
    congratulatory_message = fields.Text(string="Congratulatory Message")