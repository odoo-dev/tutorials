import hashlib
import base64
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

    name = fields.Char(string='Reference', required=True, default='New', copy=False, readonly=True, tracking=True)

    state = fields.Selection([('draft', 'Draft'), ('sending', 'Sending'), ('queued', 'Queued'),
                              ('running', 'Running'), ('done', 'Done'), ('failed', 'Failed'), ],
                             default='draft', tracking=True, string='Status')

    # Input files
    tds_file = fields.Binary(string='TDS/TCS Input File', required=True, attachment=True,
                             help='Upload .txt or .fvu file')
    tds_filename = fields.Char(string='Filename')

    csi_file = fields.Binary(string='Challan File (.csi)', attachment=True,
                             help='Upload .csi file for correction statements')
    csi_filename = fields.Char(string='CSI Filename')

    # Database identification
    db_instance_uuid = fields.Char(string='Database Instance UUID', readonly=True, copy=False,
                                   default=lambda self: self._default_db_instance_uuid(),
                                   help='Odoo database instance UUID (from ir.config_parameter)')

    db_name = fields.Char(string='Database Name', readonly=True, copy=False,
                          default=lambda self: self._default_db_name(),
                          help='PostgreSQL database name')

    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
                                 default=lambda self: self.env.company, help='Company this record belongs to')

    server_url = fields.Char(string='Server URL', default='http://localhost:8070',
                             help='TDS server base URL (hardcoded default, no config param yet)')

    # Checksum
    checksum = fields.Char(string='Checksum (SHA-256)', readonly=True, copy=False,
                           help='SHA-256 checksum of the uploaded TDS file, computed client-side before sending')

    # Webhook / Async
    server_validation_id = fields.Integer(string='Server Validation ID', readonly=True, copy=False,
                                          help='ID of the validation record created on the server', )

    webhook_received = fields.Boolean(string='Webhook Received', readonly=True, default=False,
                                      help='Whether the server has POSTed results back via webhook', )

    output_attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='tds_client_att_rel',
                                             column1='client_id', column2='att_id', string='Output Files',
                                             readonly=True)
    error_message = fields.Text(string='Error Message', readonly=True)

    # Static helpers
    @staticmethod
    def _compute_checksum(file_b64):
        """Compute SHA-256 hex digest of a base64-encoded file."""
        raw_bytes = base64.b64decode(file_b64)
        return hashlib.sha256(raw_bytes).hexdigest()

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

    # Validation helpers
    @staticmethod
    def _is_valid_tds_name(name):
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
                'warning': {'title': 'Invalid TDS filename', 'message': 'TDS file must end with .txt or .fvu'}
            }

    @api.onchange('csi_filename')
    def onchange_csi_filename(self):
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            self.csi_file = False
            self.csi_filename = ""
            return {
                'warning': {'title': 'Invalid CSI filename', 'message': 'Challan file must end with .csi', }
            }

    # Actions
    def action_send_to_server(self):
        self.ensure_one()
        # Pre flight checks
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

        self.checksum = self._compute_checksum(tds_b64)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
        webhook_url = f'{base_url}/api/tds/webhook' if base_url else ''

        payload = {
            'tds_file_b64': tds_b64,
            'checksum': self.checksum,
            'webhook_url': webhook_url,
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

        self.write({'state': 'sending', 'error_message': False, 'checksum': self.checksum, })
        self.env.cr.commit()

        server_url = self.server_url.rstrip('/')
        api_url = f'{server_url}/api/tds/generate'
        _logger.info("TDS Client: POST → %s", api_url)

        try:
            response = requests.post(api_url, json={'jsonrpc': '2.0', 'params': payload}, timeout=20)
            resp_json = response.json()

            if 'error' in resp_json:
                err_msg = resp_json['error'].get('message', resp_json['error'].get('data', {}).get('message', str(
                    resp_json['error'])))
                self._handle_error(f"Server error: {err_msg}")
                return

            result = resp_json.get('result', {})
        except requests.exceptions.ConnectionError:
            self._handle_error(f"Cannot connect to server at {server_url}")
            return
        except requests.exceptions.Timeout:
            self._handle_error("Server timeout")
            return
        except ValueError as e:
            self._handle_error(f"Invalid JSON response from server: {e}")
            return
        except Exception as e:
            self._handle_error(str(e))
            return

        # Parse response
        if result.get('status') != 'ok':
            message = result.get('message', 'Unknown error from server')
            _logger.error("Server returned error: %s (full result: %s)", message, result)
            self._handle_error(message)
            return

        # Async response - store server validation_id
        data = result.get('data', {})
        validation_id = data.get('validation_id')

        self.write({'server_validation_id': validation_id, })

        self.message_post(body=f"⏳ Request queued on srver (ref: {data.get('reference', '')}). "
                               f""f"Results will arrive via webhook when processing completes.",
                          subtype_xmlid='mail.mt_note')

    def _handle_error(self, message):
        _logger.error("TDS Client Error: %s", message)
        self.write({'state': 'failed', 'error_message': message, })
        raise UserError(message)

    def action_reset(self):
        self.write({'state': 'draft',
                    'error_message': False,
                    'output_attachment_ids': [(5, 0, 0)],
                    'server_validation_id': False,
                    'webhook_received': False, })
