from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    is_recognition_required = fields.Boolean(
        compute="_compute_is_recognition_required"
    )

    @api.depends('sale_order_id.invoice_ids')
    def _compute_is_recognition_required(self):
         self.is_recognition_required = self.env['account.move.line'].search([
            ('move_id', 'in', self.sale_order_id.invoice_ids.ids),
            ('account_id.internal_group', 'in', ['income', 'expense']),
            ('parent_state', '=', 'posted'),
            ('recognition_date', '!=', self.date_start)
        ])

    def open_cut_off_wizard(self):
        journal_items = self.env['account.move.line'].search([
            ('move_id', 'in', self.sale_order_id.invoice_ids.ids),
            ('account_id.internal_group', 'in', ['income', 'expense']),
            ('parent_state', '=', 'posted'),
            ('recognition_date', '!=', self.date_start)
        ])
        action = self.env['ir.actions.act_window']._for_xml_id('account.account_automatic_entry_wizard_action')
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx.pop('default_journal_id', None)
        ctx['active_ids'] = journal_items.ids
        ctx['active_model'] = 'account.move.line'
        ctx['default_action'] = 'change_period'
        ctx['default_date'] = self.date_start
        action['context'] = ctx
        return action
