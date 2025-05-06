# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleBranch(models.Model):
    _name = 'sale.branch'
    _description = 'Sale Branch'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string="Sequence")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence = self.env['ir.sequence'].create({
                'name': vals['name'],
                'code': vals['code'],
                'prefix': vals['code'],
                'padding': 5
            })
            vals.update({'sequence_id': sequence.id})
        return super().create(vals_list)
