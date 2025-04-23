# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    project_id = fields.Many2one("project.project")
