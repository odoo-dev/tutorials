# frtan case study: server framework
from typing import Self

from odoo import models, fields, api, Command
from odoo.orm.types import ValuesType

class SaleBranch(models.Model):
    _name = 'sale.branch'
    _description = 'Sales\' branches for multiple shop branches'

    name = fields.Char(string='Name', required=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence')
    code = fields.Char(string='Code')

    @api.model
    def create(self, vals_list: list[ValuesType]):
        for vals in vals_list:
            sequence = self.env['ir.sequence'].create({
                'name': vals['name'],
                'code': vals['code'],
                'implementation': 'standard',
                'number_increment': 1,
                'number_next': 1,
                'padding': 5,
                'prefix': vals['code']
            })
            vals.update({'sequence_id': sequence.id})
        return super().create(vals_list)