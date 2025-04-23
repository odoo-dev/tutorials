# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ScheduleLine(models.Model):
    _name = "schedule.line"
    _description = "Schedule Lines"

    project_id = fields.Many2one("project.project", readonly=True)
    working_day = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Working Days",
        required=True
    )
    duration = fields.Float("Lecture Duration", default=55.00)
    subject_ids = fields.Many2many("subject.subject", required=True)
    lecturer_ids = fields.Many2many("res.users")
