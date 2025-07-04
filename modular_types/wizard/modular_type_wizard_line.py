from odoo import models, fields


class ModularTypeWizardLine(models.TransientModel):
    _name = "modular.type.wizard.line"

    wizard_id = fields.Many2one(
        "modular.type.wizard", required=True, ondelete="cascade"
    )
    modular_type_id = fields.Many2one(comodel_name="modular.type", required=True)
    value = fields.Integer(string="Value")
