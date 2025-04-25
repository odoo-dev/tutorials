# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from datetime import datetime
from odoo import _
from odoo.http import Controller, request, route


class EventController(Controller):
    @route('/my/lectures', type='http', auth="user", website=True)
    def my_lectures(self):
        logged_in_user = request.env.user
        registrations = request.env['event.registration'].sudo().search([
            ('partner_id', '=', logged_in_user.partner_id.id)
        ])
        events = registrations.mapped('event_id')

        events_data = [
            {
                "id": event.id,
                "title": event.name,
                "start": event.date_begin.strftime('%Y-%m-%dT%H:%M:%S'),
                "end": event.date_end.strftime('%Y-%m-%dT%H:%M:%S'),
                "lecturer": event.user_id.name if event.user_id else "",
                "project_id": event.id,
                "isCancelled": event.stage_id.name == "Cancelled",
                "attended": any(reg.state == "done" for reg in registrations.filtered(lambda r: r.event_id == event))
            }
            for event in events
        ]

        return request.render("schedule_plan.lecture_calendar_template", {
            "events_json": json.dumps(events_data),
            "current_user": json.dumps({
                "id": logged_in_user.id,
                "name": logged_in_user.name,
            }),
        })

    @route('/my/attendance/report', type='http', auth="user", website=True)
    def my_report(self):
        logged_in_user = request.env.user
        partner = logged_in_user.partner_id
        project = partner.project_id

        registrations = request.env['event.registration'].sudo().search([
            ('partner_id', '=', partner.id),
            ('event_id.name', 'not ilike', "%BREAK%"),
            ('event_id.project_id', '=', project.id)
        ])

        attended_count = 0
        not_attended_count = 0
        cancelled_count = 0

        current_time = datetime.now()

        for reg in registrations:
            event = reg.event_id
            if reg.state == 'done':
                attended_count += 1
            elif event.date_end < current_time:
                not_attended_count += 1
            if event.stage_id.name == 'Cancelled':
                cancelled_count += 1

        address_parts = [
            partner.street or '',
            partner.street2 or '',
            partner.zip or '',
        ]

        duration = f"{project.date_start.strftime('%d/%m/%Y')} {_('to')} {project.date.strftime('%d/%m/%Y')}" if project else ""
        attendance = "{:.2f}".format(attended_count / (attended_count + not_attended_count)
                                     * 100) if (attended_count + not_attended_count) > 0 else "0.00"

        user_details = {
            "name": logged_in_user.name,
            "email": logged_in_user.email,
            "phone": logged_in_user.phone,
            "address": ', '.join(filter(None, address_parts)),
            "project": project.name if project else '',
            "duration": duration,
            "image": partner.avatar_128,
            "data": [attended_count, not_attended_count, cancelled_count],
            "attendance": float(attendance),
        }

        return request.render("schedule_plan.student_report_template", {"user": user_details})
