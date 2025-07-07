from odoo import Command, fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    selected_modular_type_ids = fields.Many2many(
        'product.modular.type', compute='_compute_selected_modular_type_ids', readonly=True
    )

    def _compute_selected_modular_type_ids(self):
        for bom in self:
            modular_types = bom.bom_line_ids.mapped('modular_type_id')
            bom.selected_modular_type_ids = [Command.set(modular_types.ids)]
