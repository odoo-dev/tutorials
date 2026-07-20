import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class TdsValidation(models.Model):
    _name = 'tds.validation'
    _description = 'TDS FVU Validation'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True, default='New')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft', tracking=True)

    tds_file = fields.Binary(string='TDS/TCS Input File', required=True, attachment=True)
    tds_filename = fields.Char(string='Filename')

    output_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='tds_val_att_rel', column1='val_id',
                                             column2='att_id', string='Output Files', readonly=True)

    error_message = fields.Text(string='Error Message', readonly=True)
