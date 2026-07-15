"""
TDS Client Model
-----------------
Odoo model that calls the TDS Server API (POST /api/tds/generate).
Uploads TDS/TCS files and optional CSI file, authenticates with the
server, validates checksums, and receives FVU output + execution log.
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

    # ── Webhook ───────────────────────────────────────────────────
    auto_webhook = fields.Boolean(
        string='Auto Register Webhook',
        default=True,
        help='Automatically send the webhook URL to the server for callback'
    )
    webhook_url = fields.Char(
        string='Webhook URL',
        help='URL where the server should POST results (auto-computed if empty)'
    )

    # ── Server connection ─────────────────────────────────────────
    server_url = fields.Char(
        string='Server URL',
        help='TDS server base URL (leave empty to use system parameter)'
    )
    server_login = fields.Char(
        string='Server Login',
        help='Odoo login for server authentication'
    )
    server_password = fields.Char(
        string='Server Password',
        help='Odoo password for server authentication'
    )
    server_db = fields.Char(
        string='Server Database',
        help='Odoo database name on the remote server'
    )
    timeout = fields.Integer(
        string='Timeout (seconds)',
        default=300,
        help='HTTP request timeout in seconds'
    )

    # ── Server response ───────────────────────────────────────────
    server_state = fields.Char(string='Server State', readonly=True)
    server_reference = fields.Char(string='Server Reference', readonly=True)
    server_validation_id = fields.Integer(string='Server Validation ID', readonly=True)
    output_attachment_ids = fields.Many2many(
        'ir.attachment',
        'tds_client_att_rel', 'client_id', 'att_id',
        string='Output Files', readonly=True
    )
    error_message = fields.Text(readonly=True)
    execution_log = fields.Text(
        string='Server Execution Log',
        readonly=True,
        help='Step-by-step log from the TDS validation server'
    )
    raw_response = fields.Text(
        string='Raw Server Response',
        readonly=True,
        help='Full JSON response from the TDS server'
    )
    response_time = fields.Float(
        string='Response Time (s)',
        readonly=True,
        help='Total server response time in seconds'
    )

    # ── Config helpers ────────────────────────────────────────────
    @api.model
    def _get_param(self, key, default=''):
        return self.env['ir.config_parameter'].sudo().get_param(key, default)

    def _get_server_url(self):
        return (self.server_url or self._get_param('tds_client.server_url', 'http://localhost:8070')).rstrip('/')

    def _get_server_login(self):
        return self.server_login or self._get_param('tds_client.server_login', 'admin')

    def _get_server_password(self):
        return self.server_password or self._get_param('tds_client.server_password', 'admin')

    def _get_server_db(self):
        return self.server_db or self._get_param('tds_client.server_db', 'rd-TDS')

    def _get_timeout(self):
        return self.timeout or int(self._get_param('tds_client.timeout', '300'))

    # ── Checksum ──────────────────────────────────────────────────
    @staticmethod
    def _ensure_b64_str(val):
        if val is None:
            return ''
        if isinstance(val, bytes):
            return val.decode('ascii')
        return str(val)

    @staticmethod
    def _compute_checksum(tds_b64, csi_b64=None):
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
        """Authenticate with server, send files, collect execution log + outputs."""
        self.ensure_one()

        # ── Pre-flight checks ──
        if self.state == 'sending':
            raise UserError('Request already in progress.')
        if not self.tds_file:
            raise UserError('Upload TDS/TCS Input File.')
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            raise UserError('TDS file must end with .txt or .fvu')
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            raise UserError('Challan file must end with .csi')

        # ── 1. Prepare payload ──
        tds_b64 = self._ensure_b64_str(self.tds_file)
        csi_b64 = self._ensure_b64_str(self.csi_file) if self.csi_file else None

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

        # ── Add webhook URL if auto-webhook is enabled ──
        webhook_url = self.webhook_url
        if self.auto_webhook and not webhook_url:
            # Auto-compute webhook URL from the current instance
            import socket
            hostname = socket.gethostname()
            # Try to get the actual IP or use localhost
            try:
                ip = socket.gethostbyname(hostname)
            except Exception:
                ip = 'localhost'
            port = '8909'
            webhook_url = f'http://{ip}:{port}/api/tds/webhook/receive'
        if webhook_url:
            payload['webhook_url'] = webhook_url
            _logger.info("TDS Client: Webhook URL registered: %s", webhook_url)

        # ── 2. State → Sending ──
        self.write({
            'state': 'sending',
            'error_message': False,
            'execution_log': False,
            'checksum': checksum_val or False,
            'raw_response': False,
            'server_state': False,
            'server_reference': False,
            'server_validation_id': False,
            'response_time': 0,
        })
        self.env.cr.commit()

        # ── 3. Build server URL ──
        import time
        start_time = time.time()
        server_url = self._get_server_url()
        api_url = f'{server_url}/api/tds/generate'
        auth_url = f'{server_url}/web/session/authenticate'

        _logger.info(
            "TDS Client: Sending to %s (request_id=%s, checksum=%s)",
            api_url, self.request_id, checksum_val or 'N/A',
        )

        try:
            session = requests.Session()

            # ── 3a. Authenticate ──
            _logger.info("TDS Client: Authenticating at %s", auth_url)
            auth_payload = {
                'jsonrpc': '2.0',
                'params': {
                    'db': self._get_server_db(),
                    'login': self._get_server_login(),
                    'password': self._get_server_password(),
                }
            }
            auth_resp = session.post(auth_url, json=auth_payload, timeout=30)

            if auth_resp.status_code != 200:
                self._handle_error(
                    f"Server auth failed (HTTP {auth_resp.status_code})",
                )
                return

            auth_data = auth_resp.json()
            if auth_data.get('error'):
                err_detail = auth_data['error'].get('data', {}).get('message', str(auth_data['error']))
                self._handle_error(f"Server auth error: {err_detail}")
                return

            # ── 3b. Send TDS validation request (JSON-RPC) ──
            _logger.info("TDS Client: Sending TDS validation to %s", api_url)
            gen_payload = {
                'jsonrpc': '2.0',
                'params': payload,
            }

            gen_resp = session.post(
                api_url,
                json=gen_payload,
                timeout=self._get_timeout(),
            )

            elapsed = time.time() - start_time

            if gen_resp.status_code != 200:
                self._handle_error(
                    f"Server returned HTTP {gen_resp.status_code} after {elapsed:.1f}s",
                    response_time=elapsed,
                )
                return

            # Parse JSON-RPC response
            resp_data = gen_resp.json()
            api_result = resp_data.get('result', resp_data)

        except requests.exceptions.ConnectionError as e:
            self._handle_error(f"Cannot connect to TDS server at {server_url}: {e}")
            return
        except requests.exceptions.Timeout:
            self._handle_error(f"TDS server timeout ({self._get_timeout()}s) at {api_url}")
            return
        except requests.exceptions.RequestException as e:
            self._handle_error(f"HTTP request failed: {e}")
            return
        except (json.JSONDecodeError, ValueError) as e:
            self._handle_error(f"Invalid JSON response from server: {e}")
            return

        # ── 4. Parse response ──
        status = api_result.get('status', 'error')
        message = api_result.get('message', '')
        data = api_result.get('data', {})

        # Store raw response
        try:
            raw = json.dumps(api_result, indent=2, default=str)
        except Exception:
            raw = str(api_result)

        # Check server-level error
        if status != 'ok':
            self._handle_error(
                f"Server returned error: {message}",
                raw_response=raw,
                server_state=data.get('state', ''),
                response_time=elapsed,
            )
            return

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

        # ── 6. Update record with response ──
        exec_log = data.get('execution_log', '')
        self.write({
            'state': 'done',
            'server_state': data.get('state', ''),
            'server_reference': data.get('reference', ''),
            'server_validation_id': data.get('validation_id', False),
            'output_attachment_ids': [(6, 0, att_ids)],
            'execution_log': exec_log,
            'raw_response': raw,
            'checksum_valid': bool(data.get('checksum_valid', False)),
            'response_time': elapsed,
        })

        # ── 7. Build chat message with full details ──
        msg_lines = [
            "━━━━ TDS Validation Complete ━━━━",
            f"✅ Server: SUCCESS",
            f"📋 Reference: {data.get('reference', 'N/A')}",
            f"🆔 Validation ID: {data.get('validation_id', 'N/A')}",
            f"⏱ Response time: {elapsed:.1f}s",
        ]

        if data.get('checksum_valid') is True:
            msg_lines.append("🔐 Checksum: VALID ✓")
        elif data.get('checksum_valid') is False:
            msg_lines.append("🔐 Checksum: INVALID ✗")

        # Output files summary
        if output_files:
            msg_lines.append(f"📎 Output files ({len(output_files)}):")
            for f in output_files:
                try:
                    raw_bytes = base64.b64decode(f['b64'])
                    size = len(raw_bytes)
                    # Show first 200 chars of txt/fvu content
                    preview = raw_bytes.decode('utf-8', errors='ignore')[:200]
                    msg_lines.append(f"  📄 {f['name']} ({size:,} bytes)")
                    if preview.strip():
                        msg_lines.append(f"  ┌─ Preview ─────────────────────")
                        for line in preview.split('\n')[:5]:
                            msg_lines.append(f"  │ {line[:150]}")
                        msg_lines.append(f"  └──────────────────────────────")
                except Exception:
                    msg_lines.append(f"  📄 {f['name']} ({len(f.get('b64','')):,} bytes base64)")

        # Execution log summary (last 20 lines)
        if exec_log:
            log_lines = exec_log.strip().split('\n')
            msg_lines.append(f"📋 Execution log ({len(log_lines)} lines):")
            # Show last 15 lines as summary
            show_lines = log_lines[-15:] if len(log_lines) > 15 else log_lines
            for line in show_lines:
                line = line.strip()
                if line:
                    msg_lines.append(f"  {line[:200]}")

        # Attach files directly to the chatter message so they're downloadable
        chatter_attachments = []
        for att in self.output_attachment_ids:
            if att.datas:
                try:
                    raw_content = base64.b64decode(att.datas)
                    chatter_attachments.append((att.name, raw_content))
                except Exception:
                    chatter_attachments.append((att.name, att.datas))

        self.message_post(
            body='\n'.join(msg_lines),
            attachments=chatter_attachments if chatter_attachments else None,
        )

    def _handle_error(self, message, raw_response=None, server_state='', response_time=0):
        """Set failed state and post error to chatter."""
        _logger.error("TDS Client error: %s", message)
        vals = {
            'state': 'failed',
            'error_message': message,
            'server_state': server_state,
            'response_time': response_time or 0,
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
            'server_reference': False,
            'server_validation_id': False,
            'execution_log': False,
            'raw_response': False,
            'output_attachment_ids': [(5, 0, 0)],
            'checksum_valid': False,
            'response_time': 0,
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
