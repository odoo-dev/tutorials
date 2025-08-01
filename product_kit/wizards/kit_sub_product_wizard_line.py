# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class KitSubProductWizardLine(models.TransientModel):
    _name = "kit.sub.product.wizard.line"
    _description = "Kit Sub Product Wizard Line"

    wizard_id = fields.Many2one("kit.sub.product.wizard")
    product_id = fields.Many2one("product.product", string="Product")
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Price")
