# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Venue(models.Model):
    _name = "venue"
    _description = "Lecture Venue"

    name = fields.Char("Room Name")
