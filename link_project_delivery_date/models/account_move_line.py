from odoo import fields, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    recognition_date = fields.Date(string="recognition Date", help="Reloaded date from Planned date of corresponding project of sale order")

    def action_automatic_entry(self, default_action=None):
        result = super().action_automatic_entry(default_action)
        ctx = dict(result.get('context', {}))

        project = self.move_id.line_ids.sale_line_ids.order_id.project_id
        if project and project.date_start:
            ctx['default_date'] = project.date_start

        result['context'] = ctx

        return result
