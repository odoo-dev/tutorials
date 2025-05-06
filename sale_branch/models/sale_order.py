# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    branch_id = fields.Many2one(
        comodel_name='sale.branch',
        string='Branch')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sale_branch = self.env['sale.branch'].browse(vals['branch_id'])
            if sale_branch:
                sequence = sale_branch.sequence_id
                vals.update({'name': sequence.next_by_code(sequence.code)})
        return super().create(vals_list)
