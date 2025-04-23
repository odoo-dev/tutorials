# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    def mark_as_attended(self):
        active_property_ids = self.env.context.get("active_ids", [])

        if not active_property_ids:
            return

        attendies = self.env["event.registration"].browse(active_property_ids)

        if attendies:
            attendies.write({'state': 'done'})
