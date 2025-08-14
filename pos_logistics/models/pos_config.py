from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    congratulatory_text = fields.Char(
        string="Congratulatory text", default="congrats", help="Will be printed in POS footer")
