# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Add different tags to a property like cozy, spacious, etc."

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'Tag with this name already exists, try another name.')
    ]
