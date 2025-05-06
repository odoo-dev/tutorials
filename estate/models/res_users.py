# -*- coding: utf-8 -*-

from odoo import fields, models


class Users(models.Model):
    _name = 'res.users'
    _inherit = ['res.users']

    property_ids = fields.One2many(
        comodel_name='estate.property',
        inverse_name='salesperson_id',
        string="Properties",
        domain="[('state', 'in', ['new', 'offer_received'])]")  # Add a domain to the field so it only lists the available properties (Ch. 12)
