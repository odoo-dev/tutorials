# -*- coding: utf-8 -*-

from odoo import api, models, fields
from datetime import timedelta


class BatchInformation(models.Model):
    _name = 'batch.information'
    _description = 'Batch Information'

    picking_id = fields.Many2one('stock.picking', string='Picking')
    product_id = fields.Many2one('product.product', string='Product')
    batch_number = fields.Char(string="Batch Number")
    date_recipt = fields.Date(string="Date of Receipt")
    date_expiry = fields.Date(string="Expiry Date")
    supplier_id = fields.Many2one('res.partner', string='Destination Location', domain=[
                                  ('supplier_rank', '>', 0)])
    expiry_option = fields.Selection([
        ('not_available', 'Expiry Not Available'),
        ('after_opening', 'Expiry after opening the bottle')
    ], string='Expiry Option')
    is__check_activity_batch_number = fields.Boolean(
        'Batch Activity For Batch Number', default=False)
    is_check_activity_expiry_duration = fields.Boolean(
        'Batch Activity Expiry Duration', default=False)
    done_quantity = fields.Integer('Done Quantity')
    user_id = fields.Many2one(
        'res.users', 'Validated By', tracking=True,
        default=lambda self: self.env.user, copy=False
    )

    @api.model
    def _check_activity_batch_number(self):
        search_batch = self.env['batch.information'].search([
            ('batch_number', '=', False),
            ('is__check_activity_batch_number', '=', False)
        ])

    def _check_activity_expiry_duration(self):
        expiry_duration = int(self.env['ir.config_parameter'].get_param(
            'batch_receipt_tracking.expiry_duration', default=0))
        search_batch = self.env['batch.information'].search([
            ('batch_number', '!=', False),
            ('date_expiry', '!=', False),
            ('expiry_option', '!=', 'not_available'),
            ('is_check_activity_expiry_duration', '=', False)
        ])
