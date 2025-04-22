# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Schedule Plan",
    "summary": "Module to manage and schedule plans",
    "description": "This module enables efficient scheduling and management of projects, subjects, and events within Odoo.",
    "author": "Odoo",
    "website": "https://www.odoo.com",
    "version": "1.0",
    "depends": ["base", "project", "event", "hr", "contacts", "website"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/event_registration_views.xml",
        "views/project_project_views.xml",
        "views/subject_views.xml",
        "wizard/schedule_plan_project_wizard_views.xml",
        "views/res_users_views.xml",
        "views/event_event_views.xml",
        "views/event_event_template.xml",
        "views/schedule_plan_dashboard_views.xml",
        "data/ir_cron_data.xml",
        "data/website_menu_data.xml"
    ],
    'assets': {
        'web.assets_frontend': [
            'schedule_plan/static/src/js/events_calendar.js',
        ],
        'web.assets_backend': [
            'schedule_plan/static/src/components/**/*',
            'schedule_plan/static/src/js/tours/schedule_plan_tour.js',
        ],
    },
}
