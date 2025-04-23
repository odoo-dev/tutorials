# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class ScheduleDashboard(models.Model):
    _name = 'schedule.dashboard'
    _description = 'Schedule Plan Dashboard'
    _order = 'id desc'

    name = fields.Char("Title")
    user_id = fields.Many2one(
        'res.users', string='Author', default=lambda self: self.env.user)
    color = fields.Integer(
        export_string_translation=False)
    project_id = fields.Many2one(
        'project.project', export_string_translation=False)
    total_events = fields.Integer("Task Count", readonly=True)
    completed_events = fields.Integer("Closed Task Count", readonly=True)
    subject_count = fields.Integer("Subjects")
    completion_percentage = fields.Float(
        "Completion (%)", compute="_compute_completion_percentage")

    @api.depends("total_events", "completed_events")
    def _compute_completion_percentage(self):
        for record in self:
            if record.total_events > 0:
                record.completion_percentage = (
                    record.completed_events / record.total_events) * 100
            else:
                record.completion_percentage = 0.0

    def subject_list_view_action(self):
        return {
            "name": _("%(name)s Subjects", name=self.user_id.name),
            "type": "ir.actions.act_window",
            "view_mode": "list",
            "res_model": "subject.subject",
            "target": "current",
            "domain": [("faculty_ids", "in", self.user_id.id)],
        }

    def event_list_view_action(self):
        return {
            "name": _("%(name)s Events", name=self.user_id.name),
            "type": "ir.actions.act_window",
            "view_mode": "calendar",
            "res_model": "event.event",
            "target": "current",
            "domain": [("user_id", "=", self.user_id.id)],
        }
