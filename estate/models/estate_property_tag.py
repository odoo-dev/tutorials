# -*- coding: utf-8 -*-

from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Property Tag'
    _order = 'sequence asc, name asc'
    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The name must be unique.'),
    ]

    name = fields.Char(required=True, string="Property Tag")
    color = fields.Integer()
    sequence = fields.Integer(default=1, help="Used to order stages. Lower is better.")
