from odoo import models, fields, api

class Project(models.Model):
    _inherit = "project.project"

    is_reload_required = fields.Boolean(compute="_compute_is_reload_required")

    @api.depends('sale_order_id.invoice_ids')
    def _compute_is_reload_required(self):
        move_lines = self.env['account.move.line'].search([
            ('move_id', 'in', self.sale_order_id.invoice_ids.ids),
            ('account_id.internal_group', 'in', ['income', 'expense']),
            ('parent_state', '=', 'posted'),
            ('date_reloaded', '!=', self.date_start)
        ])

        if not move_lines:
            self.is_reload_required = False
        else:
            self.is_reload_required = True

    def open_cutoff_wizard(self):
        # breakpoint()

        move_lines = self.env['account.move.line'].search([
            ('move_id', 'in', self.sale_order_id.invoice_ids.ids),
            ('account_id.internal_group', 'in', ['income', 'expense']),
            ('parent_state', '=', 'posted'),
            ('date_reloaded', '!=', self.date_start)
        ])

        print(move_lines)

        if not move_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Invalid Operation',
                    'message': 'No possible action found with the selected lines.',
                    'sticky': False,
                }
            }

        action = self.env.ref('account.account_automatic_entry_wizard_action').read()[0]

        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx.pop('default_journal_id', None)
        ctx['active_ids'] = move_lines.ids
        ctx['active_model'] = 'account.move.line'
        ctx['default_action'] = 'change_period'
        ctx['default_date'] = self.date_start

        action['context'] = ctx
        return action
