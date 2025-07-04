from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    modular_type_id = fields.Many2one(
        comodel_name="modular.type",
        readonly=False,
    )

    allowed_modular_type_ids = fields.Many2many(
        related="product_id.modular_type_ids", readonly=False
    )
