# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from odoo import _, api, fields, models
from odoo.exceptions import UserError

STATUS_COLOR = {
    'on_track': 20,  # green / success
    'at_risk': 22,  # orange
    'off_track': 23,  # red / danger
    'on_hold': 21,  # light blue
    'done': 24,  # purple
    False: 0,  # default grey -- for studio
    'to_define': 0,
}


class ProjectProject(models.Model):
    _inherit = 'project.project'

    schedule_line_ids = fields.One2many(
        comodel_name='schedule.line', inverse_name='project_id')
    has_schedule_lines = fields.Boolean(
        compute="_compute_has_schedule_lines", store=True)
    event_count = fields.Integer(
        string="Event Count", compute="_compute_event_count")
    done_event_count = fields.Integer(
        'Done Tasks', compute='_compute_event_count', export_string_translation=False)
    event_completion_percentage = fields.Float(
        compute="_compute_event_completion_percentage", export_string_translation=False)

    def _compute_event_count(self):
        today = datetime.today()
        for project in self:
            project.event_count = self.env['event.event'].search_count([
                ('project_id', '=', project.id)
            ])
            project.done_event_count = self.env['event.event'].search_count([
                ('project_id', '=', project.id),
                ('date_begin', '<', today)
            ])

    @api.depends("schedule_line_ids")
    def _compute_has_schedule_lines(self):
        for record in self:
            record.has_schedule_lines = bool(record.schedule_line_ids)

    @api.depends("event_count", "done_event_count")
    def _compute_event_completion_percentage(self):
        for project in self:
            project.event_completion_percentage = (
                (project.done_event_count / project.event_count)
                if project.done_event_count > 0 else 0
            )

    def action_schedule_plan(self):
        if not (self.date_start or self.date):
            raise UserError(
                _("Please set the project plan date before generating the schedule."))
        isEventPlanned = self.env["event.event"].search(
            [("project_id", "=", self.id)])

        if isEventPlanned:
            raise UserError(_("Schedule Already Planned"))
        if self.schedule_line_ids:
            workingDays = self.schedule_line_ids.mapped(
                lambda line: line.working_day)
            if len(workingDays) != len(set(workingDays)):
                raise UserError(
                    _("There are duplicate working days in the schedule. Please ensure that each working day is unique."))

        date_project_start = self.date_start
        date_project_end = self.date
        duration_diff = (date_project_end - date_project_start).days

        memoized_schedules = {}

        availability_details = self.get_daywise_schedule(
            number_of_slots=5, slot_duration=self.schedule_line_ids[0].duration)

        for __ in range(duration_diff):
            weekday = date_project_start.weekday()

            if weekday not in memoized_schedules:
                schedule_line = self.schedule_line_ids.search(
                    [('working_day', '=', weekday), ('project_id', '=', self.id)])
                if schedule_line:
                    subjects = list(schedule_line.subject_ids)
                    available_slots = list(availability_details.get(
                        weekday, {}).get('available_slots', []))
                    break_slots = list(availability_details.get(
                        weekday, {}).get('break_slots', []))

                    memoized_schedules[weekday] = self.time_schedule(
                        subjects, date_project_start, available_slots, break_slots, schedule_line.duration)

            elif weekday in memoized_schedules:
                event_list = memoized_schedules[weekday]

                for event_id in event_list:
                    event = self.env["event.event"].browse(event_id)
                    if event.exists():
                        new_start_time = datetime.combine(
                            date_project_start, event.date_begin.time())
                        new_end_time = datetime.combine(
                            date_project_start, event.date_end.time())
                        self.env["event.event"].create({
                            "name": event.name,
                            "date_begin": new_start_time,
                            "date_end": new_end_time,
                            "user_id": event.user_id.id,
                            "description": event.description,
                            "project_id": self.id
                        })

            date_project_start += relativedelta(days=1)

    def action_view_related_events(self):
        return {
            'name': "Related Events",
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
            'view_mode': 'calendar',
            'domain': [('project_id', '=', self.id)],
            'context': dict(self.env.context, default_project_id=self.id),
        }

    def action_edit_project(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Edit Project',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def get_daywise_schedule(self, slot_duration=55, number_of_slots=None):
        employee = self.env["hr.employee"].search(
            [('work_contact_id', '=', self.env.user.partner_id.id)]
        )

        if not employee.resource_calendar_id:
            return {}

        calendar_id = employee.resource_calendar_id.id

        calendar_lines = self.env["resource.calendar.attendance"].search([
            ('calendar_id', '=', calendar_id),
            ('day_period', '!=', 'lunch')
        ])

        daywise_schedule = defaultdict(
            lambda: {"start_time": None, "end_time": None,
                     "break_slots": [], "available_slots": []}
        )

        for line in calendar_lines:
            day = int(line.dayofweek)
            start_hour = int(line.hour_from)
            start_minute = int((line.hour_from % 1) * 60)
            end_hour = int(line.hour_to)
            end_minute = int((line.hour_to % 1) * 60)

            start_time = f"{start_hour:02}:{start_minute:02}"
            end_time = f"{end_hour:02}:{end_minute:02}"

            if not daywise_schedule[day]["start_time"] or start_time < daywise_schedule[day]["start_time"]:
                daywise_schedule[day]["start_time"] = start_time

            if not daywise_schedule[day]["end_time"] or end_time > daywise_schedule[day]["end_time"]:
                daywise_schedule[day]["end_time"] = end_time

        break_lines = self.env["resource.calendar.attendance"].search([
            ('calendar_id', '=', calendar_id),
            ('day_period', '=', 'lunch')
        ])

        for break_line in break_lines:
            day = int(break_line.dayofweek)
            break_start = f"{int(break_line.hour_from):02}:{int((break_line.hour_from % 1) * 60):02}"
            break_end = f"{int(break_line.hour_to):02}:{int((break_line.hour_to % 1) * 60):02}"
            if (break_start, break_end) not in daywise_schedule[day]["break_slots"]:
                daywise_schedule[day]["break_slots"].append(
                    (break_start, break_end))

        for day, details in daywise_schedule.items():
            if details["start_time"] and details["end_time"]:
                details["available_slots"] = self.find_available_slots(
                    details["start_time"],
                    details["end_time"],
                    slot_duration,
                    details["break_slots"],
                    number_of_slots
                )

        return dict(daywise_schedule)

    def find_available_slots(self, start_time: str, end_time: str, duration: int, break_slots: list, number_of_slots):
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        slots = []

        break_intervals = [(datetime.strptime(b[0], "%H:%M"),
                            datetime.strptime(b[1], "%H:%M")) for b in break_slots]

        while start + timedelta(minutes=duration) <= end:
            next_slot = start + timedelta(minutes=duration)

            for b_start, b_end in break_intervals:
                if b_start < next_slot and start < b_end:
                    start = b_end
                    break
            else:
                slots.append(
                    (start.strftime('%H:%M'), next_slot.strftime('%H:%M')))
                start = next_slot

            if number_of_slots and len(slots) > number_of_slots:
                break

        return slots

    def time_schedule(self, subjects, date, available_slots, break_slots, duration=55):
        date_str = date.strftime('%Y-%m-%d')

        subject_list = list(subjects)
        slot_list = list(available_slots)

        utc_tz = pytz.UTC

        event_ids = []
        slot_iterator = iter(slot_list)

        while subject_list:
            subject = random.choice(subject_list)

            try:
                slot_temp = next(slot_iterator)
            except StopIteration:
                break

            slot = None
            if isinstance(slot_temp, tuple):
                slot = slot_temp[0]
            elif isinstance(slot_temp, str):
                slot = slot_temp
            if isinstance(slot, str):
                slot = datetime.strptime(slot, "%H:%M").time()

            local_tz = pytz.timezone(self.env.user.tz or 'UTC')
            local_datetime = datetime.combine(date, slot)

            event_start = local_tz.localize(
                local_datetime).astimezone(utc_tz).replace(tzinfo=None)
            event_end = event_start + relativedelta(minutes=duration)

            assigned_lecturer = subject.faculty_ids[0].id

            if self.schedule_line_ids:
                schedule_lecturers = set(
                    self.schedule_line_ids.mapped("lecturer_ids.id"))
                subject_faculties = subject.faculty_ids.ids

                prioritized_lecturers = list(
                    set(subject_faculties) & schedule_lecturers)

                if prioritized_lecturers:
                    assigned_lecturer = prioritized_lecturers[0]
                elif subject_faculties:
                    assigned_lecturer = subject_faculties[0]

            conflicting_event = self.env["event.event"].search([
                ("user_id", "=", assigned_lecturer),
                ("project_id", "!=", self.id),
                ("date_begin", ">=", date_str + " 00:00:00"),
                ("date_begin", "<=", date_str + " 23:59:59"),
            ])

            conflict_found = False
            for event in conflicting_event:
                existing_start_time = event.date_begin.time()
                existing_end_time = event.date_end.time()
                event_start_time = event_start.time()
                event_end_time = event_end.time()

                if existing_start_time < event_end_time and existing_end_time > event_start_time:
                    conflict_found = True
                    break

            if conflict_found:
                continue

            event_type = "Lab" if "lab" in subject.name.lower() else "Lecture"

            event = self.env["event.event"].create({
                "name": f"{event_type}: {subject.name} {subject.room_id.name if subject.room_id else 'TBD'}",
                "date_begin": event_start,
                "date_end": event_end,
                "user_id": assigned_lecturer,
                "description": f"{event_type} on {subject.name} in {subject.room_id.name if subject.room_id else 'TBD'}",
                "project_id": self.id
            })

            event_ids.append(event.id)

            subject_list.remove(subject)

        for break_slot in break_slots:
            if isinstance(break_slot, tuple):
                break_start_time = break_slot[0]
                break_end_time = break_slot[1]
            elif isinstance(break_slot, str):
                break_start_time = break_slot
                break_end_time = (datetime.strptime(break_slot, "%H:%M") +
                                  relativedelta(minutes=duration)).strftime("%H:%M")

            break_start = datetime.combine(
                date, datetime.strptime(break_start_time, "%H:%M").time())
            break_end = datetime.combine(
                date, datetime.strptime(break_end_time, "%H:%M").time())

            break_start = local_tz.localize(
                break_start).astimezone(utc_tz).replace(tzinfo=None)
            break_end = local_tz.localize(break_end).astimezone(
                utc_tz).replace(tzinfo=None)

            break_event = self.env["event.event"].create({
                "name": "BREAK",
                "date_begin": break_start,
                "date_end": break_end,
                "description": "Break time",
                "project_id": self.id
            })

            event_ids.append(break_event.id)

        return event_ids

    def schedule_plan_dashboard_action(self):
        if not self:
            return

        today = datetime.today()
        events = self.env["event.event"].search([("project_id", "=", self.id)])

        user_ids = list(set(events.mapped("user_id.id"))) if events else []

        status = self.last_update_status or "to_define"
        color = STATUS_COLOR.get(status, 0)

        for user_id in user_ids:
            # Filter events related to this user
            user_events = events.filtered(lambda e: e.user_id.id == user_id)

            total_events = len(user_events)
            completed_events = len(user_events.filtered(
                lambda e: e.date_begin < today))

            # Fetch subjects from `subject.subject` where faculty includes this user
            subjects = self.env["subject.subject"].search(
                [("faculty_ids", "in", [user_id])])
            num_subjects = len(subjects)

            update = self.env["schedule.dashboard"].search(
                [("project_id", "=", self.id), ("user_id", "=", user_id)], limit=1
            )

            if not update:
                update = self.env["schedule.dashboard"].create({
                    "project_id": self.id,
                    "user_id": user_id
                })

            update.write({
                "color": color,
                "project_id": self.id,
                "total_events": total_events,
                "completed_events": completed_events,
                "subject_count": num_subjects,
            })

        return {
            "name": _("%(name)s Dashboard", name=self.name),
            "type": "ir.actions.act_window",
            "view_mode": "kanban",
            "res_model": "schedule.dashboard",
            "target": "current",
        }
