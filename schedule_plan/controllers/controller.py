# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from odoo.http import Controller, request, route


class EventController(Controller):
    @route('/my/events', type='http', auth="user", website=True)
    def my_events(self):
        user = request.env.user
        registrations = request.env['event.registration'].sudo().search([
            ('partner_id', '=', user.partner_id.id)
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
                "attended": any(reg.state == "done" for reg in registrations.filtered(lambda r: r.event_id == event))
            }
            for event in events
        ]

        return request.render("schedule_plan.events_template", {
            "events_json": json.dumps(events_data),
            "locale": user.tz
        })
