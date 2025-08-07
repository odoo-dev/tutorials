from odoo import models, fields


class ResUser(models.Model):
    _inherit = 'res.users'
    _description = 'User'
    property_ids = fields.One2many(
        comodel_name='estate.property',
        inverse_name='user_id',
        string='Properties',
        domain=[('state', 'in', ['new', 'offer_received'])],
    )
