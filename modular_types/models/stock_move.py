from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    modular_type_id = fields.Many2one(
        comodel_name="modular.type",
        readonly=False,
    )

    allowed_modular_type_ids = fields.Many2many(
        related="product_id.modular_type_ids", readonly=False
    )

    @api.depends('production_id.bom_id.bom_line_ids')
    def _compute_modular_type_id(self):
        for line in self:
            line.modular_type_id = line.raw_material_production_id.bom_id.bom_line_ids.filtered(lambda l: l.product_id == line.product_id).modular_type_id
