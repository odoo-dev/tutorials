from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_is_congratulatory_message = fields.Boolean(related="pos_config_id.is_congratulatory_message", readonly=False)
    pos_congratulatory_message = fields.Text(related='pos_config_id.congratulatory_message', readonly=False)