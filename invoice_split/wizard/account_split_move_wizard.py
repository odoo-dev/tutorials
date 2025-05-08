# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountSplitMoveWizard(models.TransientModel):
    _name="account.split.move.wizard"
    _description = 'Split Invoice Wizard'

    parent_wizard_id = fields.Many2one(
        comodel_name='account.split.wizard'
    )
    child_wizard_id = fields.Many2one(
        comodel_name='account.split.wizard'
    )

    untaxed_amount = fields.Float(string="Untaxed Amount")
    tax_amount = fields.Float(string="Tax Amount")
    total = fields.Float(string="Total")
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
    )
    name = fields.Char(string="Label")
    price = fields.Float(string="Price")
    quantity = fields.Float(string="Quantity")
    tax = fields.Many2many(
        comodel_name='account.tax',
        string="Tax"
    )
    subtotal = fields.Float(string="Subtotal")
    is_parent_invoice = fields.Boolean(string="Is Parent Invoice")
    invoice_index = fields.Integer(string="Invoice NUmber")
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
        ('product', 'Normal'),
    ], default='product', required=True)
