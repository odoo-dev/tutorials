# licence

from odoo import fields
from odoo import models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = "Property tag"

    name = fields.Char("Tag", required=True, translate=True)
    description = fields.Text("Tag description")
    # Constraints
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)',
         'The property type name must be unique'),
    ]
