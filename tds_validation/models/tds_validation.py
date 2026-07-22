import logging

from odoo import models, fields
from odoo.exceptions import UserError

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
    csi_file = fields.Binary(
        string='Challan File (.csi)',
        attachment=True,
        help='Upload .csi file for correction statements'
    )
    csi_filename = fields.Char(string='CSI Filename')

    db_instance_uuid = fields.Char(string='Client DB UUID', readonly=True)
    db_name = fields.Char(string='Client DB Name', readonly=True)
    company_name = fields.Char(string='Client Company', readonly=True)

    output_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='tds_val_att_rel', column1='val_id',
                                             column2='att_id', string='Output Files', readonly=True)

    error_message = fields.Text(string='Error Message', readonly=True)

    # Actions
    def action_process(self):
        self.ensure_one()

        try:
            att_ids = []
            # Echo TDS file
            tds_echo_name = f'echo_{self.tds_filename or "file"}'
            att_tds = self.env['ir.attachment'].create({
                'name': tds_echo_name,
                'datas': self.tds_file,
                'res_model': self._name,
                'res_id': self.id,
                'description': 'Echo output (TDS)',
            })
            att_ids.append(att_tds.id)

            # Echo CSI file if present
            if self.csi_file:
                csi_echo_name = f'echo_{self.csi_filename or "challan.csi"}'
                att_csi = self.env['ir.attachment'].create({
                    'name': csi_echo_name,
                    'datas': self.csi_file,
                    'res_model': self._name,
                    'res_id': self.id,
                    'description': 'Echo output (CSI)',
                })
                att_ids.append(att_csi.id)

            self.write({
                'state': 'done',
                'output_attachment_ids': [(6, 0, att_ids)],
            })

            self.message_post(body=f' Echo complete - {len(att_ids)} file(s) attached.')
        except Exception as e:
            _logger.exception('TDS Validation Failed [%s]', self.name)
            self.write({
                'state': 'failed',
                'error_message': str(e),
            })
            self.message_post(body=f'Failed :{e}')
            raise UserError(str(e)) from e
