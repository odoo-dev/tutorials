import requests

from odoo import models, fields, api

import logging
import os

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

VALID_TDS_EXTENSIONS = {'.txt', '.fvu'}
VALID_CSI_EXTENSION = '.csi'


class TdsClient(models.Model):
    _name = 'tds.client'
    _description = 'TDS Validation Client'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True, default='New',
                       copy=False, readonly=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sending', 'Sending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft', tracking=True, string='Status')

    # Input files
    tds_file = fields.Binary(
        string='TDS/TCS Input File',
        required=True,
        attachment=True,
        help='Upload .txt or .fvu file'
    )
    tds_filename = fields.Char(string='Filename')

    csi_file = fields.Binary(
        string='Challan File (.csi)',
        attachment=True,
        help='Upload .csi file for correction statements'
    )
    csi_filename = fields.Char(string='CSI Filename')

    # ── Database identification
    db_instance_uuid = fields.Char(
        string='Database Instance UUID',
        readonly=True, copy=False,
        default=lambda self: self._default_db_instance_uuid(),
        help='Odoo database instance UUID (from ir.config_parameter)'
    )

    db_name = fields.Char(
        string='Database Name',
        readonly=True, copy=False,
        default=lambda self: self._default_db_name(),
        help='PostgreSQL database name'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True, copy=False,
        default=lambda self: self.env.company,
        help='Company this record belongs to'
    )

    server_url = fields.Char(string='Server URL', default='http://localhost:8070',
                             help='TDS server base URL (hardcoded default, no config param yet)', )

    output_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='tds_client_att_rel',
                                             column1='client_id', column2='att_id', string='Output Files',
                                             readonly=True)
    error_message = fields.Text(string='Error Message', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _logger.warning("Generating new sequence for TDS Client record")
            vals['name'] = self.env['ir.sequence'].next_by_code('tds.client')
            if not vals.get('name') or vals['name'] == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('tds.client') or 'New'
        _logger.warning("Creating TDS Client records: %s", vals_list)
        return super().create(vals_list)

    @api.model
    def _default_db_instance_uuid(self):
        return self.env['ir.config_parameter'].sudo().get_param('database.uuid', '')

    @api.model
    def _default_db_name(self):
        return self.env.cr.dbname

    # ── Validation helpers
    @staticmethod
    def _is_valid_tds_name(name):
        # splitext use for split the file name in two parts like tds.txt ("tds",".txt")
        # ( _ ) is used for file store in variable, but we don't want so we assign in underscore
        _, ext = os.path.splitext(name.lower())
        return ext in VALID_TDS_EXTENSIONS

    @staticmethod
    def _is_valid_csi_name(name):
        return name.lower().endswith(VALID_CSI_EXTENSION)

    @api.onchange('tds_filename')
    def onchange_tds_file(self):
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            self.tds_file = False
            self.tds_filename = ""
            return {
                'warning': {
                    'title': 'Invalid TDS filename',
                    'message': 'TDS file must end with .txt or .fvu',
                }
            }

    @api.onchange('csi_filename')
    def onchange_csi_filename(self):
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            self.csi_file = False
            self.csi_filename = ""
            return {
                'warning': {
                    'title': 'Invalid CSI filename',
                    'message': 'Challan file must end with .csi',
                }
            }

    # ── Actions
    def action_send_to_server(self):
        self.ensure_one()
        # ── Pre checks ──
        if self.state == 'sending':
            raise UserError('Request already in progress.')
        if not self.tds_file:
            raise UserError('Upload TDS/TCS Input File.')
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            raise UserError('TDS file must end with .txt or .fvu')
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            raise UserError('Challan file must end with .csi')

        tds_b64 = self.tds_file
        if isinstance(tds_b64, bytes):
            tds_b64 = tds_b64.decode('ascii')

        payload = {
            'tds_file_b64': tds_b64,
            'tds_filename': self.tds_filename or 'tds.txt',
            'db_instance_uuid': self.db_instance_uuid or '',
            'db_name': self.db_name or '',
            'company_name': self.company_id.name or '',
        }

        if self.csi_file:
            csi_b64 = self.csi_file
            if isinstance(csi_b64, bytes):
                csi_b64 = csi_b64.decode('ascii')
            payload['csi_file_b64'] = csi_b64
            payload['csi_filename'] = self.csi_filename or 'challan.csi'

        self.write({
            'state': 'sending',
            'error_message': False,
        })
        self.env.cr.commit()

        server_url = self.server_url.rstrip('/')
        api_url = f'{server_url}/api/tds/generate'
        logging.info("TDS Client: POST → %s", api_url)

        try:
            response = requests.post(
                api_url,
                json={'jsonrpc': '2.0',
                      'params': payload},
                timeout=120,
            )
            result = response.json().get('result', {})
        except requests.exceptions.ConnectionError:
            self._handle_error(f"Cannot connect to server at {server_url}")
            return
        except requests.exceptions.Timeout:
            self._handle_error("Server timeout")
            return
        except Exception as e:
            self._handle_error(str(e))
            return

        output_files = result.get('data', {}).get('output_files', [])
        att_ids = []
        for f in output_files:
            att = self.env['ir.attachment'].create({
                'name': f['name'],
                'datas': f['b64'],
                'res_model': self._name,
                'res_id': self.id,
                'description': 'TDS FVU Output From TDS Server',
            })
            att_ids.append(att.id)

        self.write({
            'state': 'done',
            'output_attachment_ids': [(6, 0, att_ids)],
        })

        self.message_post(
            body=f" TDS/TCS Validation Complete - {len(output_files)} output file(s) received.",
            subtype_xmlid='mail.mt_note'
        )

    def _handle_error(self, message):
        _logger.error("TDS Client Error: %s", message)
        self.write({
            'state': 'failed',
            'error_message': message,
        })
        raise UserError(message)

    def action_reset(self):
        self.write({
            'state': 'draft',
            'error_message': False,
            'output_attachment_ids': [(5, 0, 0)],
        })
