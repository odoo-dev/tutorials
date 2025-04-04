from odoo import fields, models, api


class PosNote(models.Model):
    _inherit = "pos.note"
    color = fields.Integer()

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Load additional fields (color) for POS"""
        return super()._load_pos_data_fields(config_id) + ['color']

    @api.model
    def get_color(self, notes):
        color = {}
        for note in notes.split('\n'):
            if note:
                record = self.search([('name', '=', note)], limit=1)
                if record and record.color:
                    color[note] = record.color
        return color
