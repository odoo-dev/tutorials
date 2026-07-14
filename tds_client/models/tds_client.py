"""
TDS Client Model
-----------------
Odoo model that calls the TDS Server API (POST /api/tds/generate).
Uploads TDS/TCS files and optional CSI file, validates checksums,
and receives FVU output files from the remote server.
"""

import base64
import hashlib
import json
import logging
import os

import requests

from odoo import api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

VALID_TDS_EXTENSIONS = {'.txt', '.fvu'}
VALID_CSI_EXTENSION = '.csi'


class TdsClient(models.Model):
    _name = 'tds.client'
    _description = 'TDS Validation Client'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference', required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('tds.client') or 'New'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sending', 'Sending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft', tracking=True)

    # ── Input files ───────────────────────────────────────────────
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

    # ── Metadata ──────────────────────────────────────────────────
    request_id = fields.Char(
        string='Request ID',
        help='External reference from the calling system'
    )
    request_date = fields.Char(
        string='Request Date',
        help='Date in YYYY-MM-DD format'
    )
    notes = fields.Text(string='Notes')

    # ── Checksum ──────────────────────────────────────────────────
    checksum = fields.Char(
        string='Checksum',
        help='SHA-256 checksum of input files for integrity verification'
    )
    compute_checksum = fields.Boolean(
        string='Auto-compute Checksum',
        default=True,
        help='Automatically compute SHA-256 checksum before sending'
    )
    checksum_valid = fields.Boolean(
        string='Checksum Valid',
        default=False,
        readonly=True,
        help='Whether the server confirmed the checksum matched'
    )

    # ── Server response ───────────────────────────────────────────
    server_state = fields.Char(string='Server State', readonly=True)
    output_attachment_ids = fields.Many2many(
        'ir.attachment',
        'tds_client_att_rel', 'client_id', 'att_id',
        string='Output Files', readonly=True
    )
    error_message = fields.Text(readonly=True)
    raw_response = fields.Text(
        string='Raw Server Response',
        readonly=True,
        help='Full JSON response from the TDS server'
    )

    # ── Config ────────────────────────────────────────────────────
    server_url = fields.Char(
        string='Server URL',
        help='TDS server base URL (leave empty to use system parameter)'
    )

    # ── Config helper ─────────────────────────────────────────────
    @api.model
    def _get_server_url(self, record_url=None):
        """Get server URL from record field or system parameter."""
        if record_url:
            return record_url.rstrip('/')
        return self.env['ir.config_parameter'].sudo().get_param(
            'tds_client.server_url', 'http://localhost:8069'
        ).rstrip('/')

    # ── Checksum ──────────────────────────────────────────────────
    @staticmethod
    def _ensure_b64_str(val):
        """Ensure a Binary field value is returned as a base64 string."""
        if val is None:
            return ''
        if isinstance(val, bytes):
            return val.decode('ascii')
        return str(val)

    @staticmethod
    def _compute_checksum(tds_b64, csi_b64=None):
        """Compute SHA-256 checksum of decoded file bytes."""
        sha = hashlib.sha256()
        try:
            sha.update(base64.b64decode(tds_b64))
        except Exception:
            sha.update(tds_b64.encode('utf-8'))
        if csi_b64:
            try:
                sha.update(base64.b64decode(csi_b64))
            except Exception:
                sha.update(csi_b64.encode('utf-8'))
        return sha.hexdigest()

    # ── Validation helpers ────────────────────────────────────────
    @staticmethod
    def _is_valid_tds_name(name):
        _, ext = os.path.splitext(name.lower())
        return ext in VALID_TDS_EXTENSIONS

    @staticmethod
    def _is_valid_csi_name(name):
        return name.lower().endswith(VALID_CSI_EXTENSION)

    @api.onchange('tds_filename')
    def _onchange_tds_filename(self):
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            return {
                'warning': {
                    'title': 'Invalid Extension',
                    'message': 'TDS file must end with .txt or .fvu',
                }
            }

    @api.onchange('csi_filename')
    def _onchange_csi_filename(self):
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            return {
                'warning': {
                    'title': 'Invalid Extension',
                    'message': 'Challan file must end with .csi',
                }
            }

    # ── Actions ───────────────────────────────────────────────────
    def action_send_to_server(self):
        """Send files to TDS server API and collect results."""
        self.ensure_one()

        if self.state == 'sending':
            raise UserError('Request already in progress.')
        if not self.tds_file:
            raise UserError('Upload TDS/TCS Input File.')
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            raise UserError('TDS file must end with .txt or .fvu')
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            raise UserError('Challan file must end with .csi')

        # ── 1. Prepare payload ──
        # Odoo Binary fields store base64-encoded data. Normalize to string.
        tds_b64 = self._ensure_b64_str(self.tds_file)
        csi_b64 = self._ensure_b64_str(self.csi_file) if self.csi_file else None

        # Compute checksum if enabled
        checksum_val = self.checksum
        if self.compute_checksum and not checksum_val:
            checksum_val = self._compute_checksum(tds_b64, csi_b64)

        payload = {
            'tds_file_b64': tds_b64,
            'tds_filename': self.tds_filename or 'tds.txt',
            'request_id': self.request_id or '',
            'request_date': self.request_date or '',
            'notes': self.notes or '',
        }
        if csi_b64:
            payload['csi_file_b64'] = csi_b64
            payload['csi_filename'] = self.csi_filename or 'challan.csi'
        if checksum_val:
            payload['checksum'] = checksum_val

        # ── 2. State → Sending ──
        self.write({
            'state': 'sending',
            'error_message': False,
            'checksum': checksum_val or False,
            'raw_response': False,
        })
        self.env.cr.commit()

        # ── 3. Call server API ──
        server_url = self._get_server_url(self.server_url)
        api_url = f'{server_url}/api/tds/generate'

        _logger.info("TDS Client: POST %s (request_id=%s)", api_url, self.request_id)

        try:
            resp = requests.post(
                api_url,
                json={'jsonrpc': '2.0', 'method': 'call', 'params': payload},
                headers={'Content-Type': 'application/json'},
                timeout=300,
            )
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.ConnectionError as e:
            self._handle_error(f"Cannot connect to TDS server at {server_url}: {e}")
        except requests.exceptions.Timeout:
            self._handle_error(f"TDS server timeout (300s) at {api_url}")
        except requests.exceptions.RequestException as e:
            self._handle_error(f"HTTP request failed: {e}")
        except (json.JSONDecodeError, ValueError) as e:
            self._handle_error(f"Invalid JSON response from server: {e}")

        # ── 4. Parse response ──
        # JSON-RPC wraps result in "result" key
        api_result = result.get('result', result)

        status = api_result.get('status', 'error')
        message = api_result.get('message', '')
        data = api_result.get('data', {})

        # Store raw response
        try:
            raw = json.dumps(result, indent=2, default=str)
        except Exception:
            raw = str(result)

        if status != 'ok':
            self._handle_error(
                f"Server returned error: {message}",
                raw_response=raw,
                server_state=data.get('state', ''),
            )

        # ── 5. Create output attachments ──
        att_ids = []
        output_files = data.get('output_files', [])
        for f in output_files:
            att = self.env['ir.attachment'].create({
                'name': f['name'],
                'datas': f['b64'],
                'res_model': self._name,
                'res_id': self.id,
                'description': 'TDS FVU Output from Server',
            })
            att_ids.append(att.id)

        self.write({
            'state': 'done',
            'server_state': data.get('state', ''),
            'output_attachment_ids': [(6, 0, att_ids)],
            'raw_response': raw,
            'checksum_valid': data.get('checksum_valid', False),
        })
        self.message_post(
            body=f"✅ Server validation complete. "
                 f"Reference: {data.get('reference', 'N/A')}. "
                 f"{len(att_ids)} file(s) received."
        )

    def _handle_error(self, message, raw_response=None, server_state=''):
        """Set failed state and post error to chatter."""
        _logger.error("TDS Client error: %s", message)
        vals = {
            'state': 'failed',
            'error_message': message,
            'server_state': server_state,
        }
        if raw_response:
            vals['raw_response'] = raw_response
        self.write(vals)
        self.message_post(body=f"❌ {message}")
        raise UserError(message)

    def action_reset(self):
        """Reset failed record back to draft."""
        self.write({
            'state': 'draft',
            'error_message': False,
            'server_state': False,
            'raw_response': False,
            'output_attachment_ids': [(5, 0, 0)],
            'checksum_valid': False,
        })

    def action_view_raw_response(self):
        """Open raw JSON response in a popup."""
        self.ensure_one()
        if not self.raw_response:
            raise UserError('No raw response available.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Raw Server Response',
            'res_model': 'tds.client',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(self.env.ref('tds_client.view_tds_client_raw_form').id, 'form')],
            'target': 'new',
        }
