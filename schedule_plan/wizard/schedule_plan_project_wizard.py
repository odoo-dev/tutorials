# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SchedulePlanProject(models.TransientModel):
    _name = "schedule.plan.project.wizard"
    _description = "Schedule Plan Project Wizard"

    project_id = fields.Many2one(
        "project.project", domain="[('last_update_status', '=', 'on_track')]", required=True)

    def add_student(self):
        active_id = self.env.context.get('active_id')
        if not active_id:
            return

        partner = self.env["res.partner"].browse(active_id)
        partner.project_id = self.project_id.id

        events = self.env["event.event"].search(
            [("project_id", "=", self.project_id.id)])
        if events:
            vals_list = [{'event_id': event.id, 'partner_id': active_id}
                         for event in events]
            self.env['event.registration'].create(vals_list)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                    'title': _("Batch Completed Successfully"),
                    'type': 'success',
                    'message': _("Created Batch for first %(batch_size)s Event", batch_size=batch_size),
                    'sticky': False,
            },
        }
