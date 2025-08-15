from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'
    _description = 'Point of Sale Configuration'

    congratulations_message = fields.Char(
        string='Congratulations Message',
        help='Message displayed to the user when they win a prize.',
        default='Congratulations! You have won a prize!',
        required=False)
