from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    check_action_sold = fields.Char(string="Enable Sold")
