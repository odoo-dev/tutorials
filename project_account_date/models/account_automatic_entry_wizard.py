from odoo import models

class AccountAutomaticEntryWizard(models.TransientModel):
    _inherit = 'account.automatic.entry.wizard'

    def do_action(self):
        active_ids = self._context.get('active_ids', [])
        if not active_ids:
            return super(AccountAutomaticEntryWizard, self).do_action()

        move_lines = self.env['account.move.line'].browse(active_ids)
        move_lines.write({'date_reloaded': self.date})

        return super(AccountAutomaticEntryWizard, self).do_action()
