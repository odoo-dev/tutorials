# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class EventEvent(models.Model):
    _inherit = 'event.event'

    project_id = fields.Many2one('project.project')
