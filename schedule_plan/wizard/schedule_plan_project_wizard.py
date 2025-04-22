# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models
from odoo.exceptions import UserError


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

        if partner.project_id == self.project_id:
            raise UserError(
                _("Student was Already Enrolled in %(project)s", project=self.project_id.name))

        cron_job = self.env.ref("schedule_plan.ir_cron_action_schedule_plan")
        if cron_job:
            partner.project_id = self.project_id.id
            cron_job._trigger()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Student Successfully Added"),
                    'type': 'success',
                    'message': _("The student has been assigned to the project, and the scheduled attendee update has been triggered."),
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Failed to Add Student"),
                    'message': _("An error occurred while adding the student. Please check the required fields and try again."),
                    'type': 'warning',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }
