# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo.tests import TransactionCase,tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestSchedulePlan(TransactionCase):
    PROJECT_DURATION_IN_DAYS = 7
    PROJECT_START_DATE = datetime.now()
    PROJECT_END_DATE = datetime.now() + timedelta(days=PROJECT_DURATION_IN_DAYS)
    SLOT_DURATION = 55.0

    @classmethod
    def setUpClass(cls):
        super(TestSchedulePlan, cls).setUpClass()

        cls.venue = cls.env['venue'].create({
            'name': 'Room 101'
        })

        cls.faculty_1 = cls.env['res.users'].create({
            'name': 'Faculty One',
            'login': 'faculty1@example.com',
            'email': 'faculty1@example.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })

        cls.faculty_2 = cls.env['res.users'].create({
            'name': 'Faculty Two',
            'login': 'faculty2@example.com',
            'email': 'faculty2@example.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })

        cls.students = cls.env['res.partner'].create([
            {'name': 'Test Student 1', 'email': 'test1@odoo.com'},
            {'name': 'Test Student 2',
                'email': 'test2@odoo.com'},
        ])

        cls.subjects = cls.env['subject.subject'].create([
            {'name': 'Mathematics', 'room_id': cls.venue.id, 'faculty_ids': [
                (6, 0, [cls.faculty_1.id, cls.faculty_2.id])]},
            {'name': 'Physics', 'room_id': cls.venue.id,
                'faculty_ids': [(6, 0, [cls.faculty_2.id])]},
            {'name': 'Chemistry', 'room_id': cls.venue.id,
                'faculty_ids': [(6, 0, [cls.faculty_1.id])]},
            {'name': 'Biology', 'room_id': cls.venue.id,
                'faculty_ids': [(6, 0, [cls.faculty_2.id])]},
            {'name': 'Computer Science', 'room_id': cls.venue.id,
                'faculty_ids': [(6, 0, [cls.faculty_1.id])]},
        ])

        cls.projects = cls.env['project.project'].create([
            {
                'name': 'B.Tech Semester 1',
                'partner_id': cls.env.ref("base.res_partner_1").id,
                'last_update_status': 'on_track'
            },
            {
                'name': 'B.Tech Semester 2',
                'partner_id': cls.env.ref("base.res_partner_1").id,
                'last_update_status': 'off_track'
            }
        ])

        working_days = ['0', '1', '2', '3', '4']
        for index, day in enumerate(working_days):
            cls.env['schedule.line'].create({
                'project_id': cls.projects[0].id,
                'working_day': day,
                'duration': cls.SLOT_DURATION,
                'subject_ids': [(6, 0, [cls.subjects[index].id])],
            })

    def test_project_without_start_date(self):
        """
        Test that the schedule is not created if the project has no start date
        """
        project = self.projects[0]
        with self.assertRaises(UserError):
            project.action_schedule_plan()

    def test_schedule_plan_with_duplicate_days(self):
        """
        Test that the schedule is not created if it has duplicate working days
        """
        project = self.projects[0]
        project.write({
            'date_start': self.PROJECT_START_DATE,
            'date': self.PROJECT_END_DATE,
        })

        with self.assertRaises(UserError):
            self.env['schedule.line'].create({
                'project_id': project.id,
                'working_day': '0',
                'duration': self.SLOT_DURATION,
                'subject_ids': [(6, 0, [self.subjects[0].id])],
                'lecturer_ids': [(6, 0, [self.faculty_1.id])]
            })
            project.action_schedule_plan()

    def test_schedule_plan_with_valid_data(self):
        """
        Test that the schedule is created successfully with valid data
        """
        project = self.projects[0]
        project.write({
            'date_start': self.PROJECT_START_DATE,
            'date': self.PROJECT_END_DATE,
        })  

        self.env.user = self.env.ref("base.user_admin")

        project.with_user(self.env.user).action_schedule_plan()

        EVENT_COUNT = self.env['event.event'].search_count([
            ('project_id', '=', project.id),
        ])


        self.assertEqual(project.event_count,EVENT_COUNT)

    def test_student_registration_to_project_events(self):
        """
        Test the user registration in lectures.
        """
        project = self.projects[0]
        events = self.env['event.event'].search([('project_id', '=', project.id)])
        student = self.students[0]

        wizard = self.env["schedule.plan.project.wizard"].with_context(
            active_id=student.id
        ).create({'project_id': project.id})

        wizard.add_student()

        for event in events:
            self.assertIn(student.id, event.registration_ids.mapped('partner_id').ids,
                        f"Student {student.id} not found in event {event.id} registrations")
