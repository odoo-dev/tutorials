# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Subject(models.Model):
    _name = "subject.subject"
    _description = "Subject and Relative Faculty"

    name = fields.Char("Subject Name")
    room_id = fields.Many2one("venue")
    faculty_ids = fields.Many2many("res.users")
