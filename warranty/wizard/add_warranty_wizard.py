from odoo import api,fields,models
class AddWarrantyWizard(models.TransientModel):
    _name="add.warranty.wizard"
    warranty_line_ids = fields.One2many('warranty.line', 'wizard_id')
    