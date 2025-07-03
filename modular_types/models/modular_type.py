from odoo import fields, models


class ModularType(models.Model):
    _name = "modular.type"
    _description = "Product Modular Type"

    name = fields.Char(string="Module Type", required=True)
