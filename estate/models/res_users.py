from odoo import models, fields


class User(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property", "user_id", domain="['|', ('state', '=', 'new'), ('state', '=', 'offer_received')]")
