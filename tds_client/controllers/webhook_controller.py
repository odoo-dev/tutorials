"""
Webhook Receiver Controller
----------------------------
Receives POST /api/tds/webhook/receive from the TDS validation server
when validation completes. Saves output files as attachments on the
corresponding tds.client record.

The client sends its own webhook URL in the initial API request:
  webhook_url: "http://client-host:8909/api/tds/webhook/receive"
"""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TDSWebhookReceiver(http.Controller):

    @http.route('/api/tds/webhook/receive', type='jsonrpc', methods=['POST'], auth='public', csrf=False)
    def receive_webhook(self, **kwargs):
        """
        POST /api/tds/webhook/receive
        {
            "event": "validation.complete",
            "validation_id": 123,
            "reference": "TDS/2026/0001",
            "state": "done",
            "request_id": "REQ-001",
            "checksum": "...",
            "checksum_valid": true,
            "execution_log": "...",
            "error_message": "",
            "error": "",
            "output_files": [{"name": "file.fvu", "b64": "..."}]
        }

        Returns:
            {"status": "ok"}
        """
        try:
            data = request.params if hasattr(request, 'params') else kwargs
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    pass

            _logger.info("Webhook received: event=%s ref=%s state=%s",
                         data.get('event'), data.get('reference'), data.get('state'))

            request_id = data.get('request_id', '')
            validation_id = data.get('validation_id', '')
            state = data.get('state', '')
            reference = data.get('reference', '')
            exec_log = data.get('execution_log', '')
            error_msg = data.get('error', '') or data.get('error_message', '')
            checksum_valid = data.get('checksum_valid', False)
            output_files = data.get('output_files', [])

            # Find the matching tds.client record by request_id or validation_id
            domain = []
            if request_id:
                domain = [('request_id', '=', request_id)]
            if not domain and validation_id:
                domain = [('server_validation_id', '=', validation_id)]

            if not domain:
                _logger.warning("Webhook: no identifier to match record")
                return {'status': 'error', 'message': 'No request_id or validation_id'}

            client_records = request.env['tds.client'].sudo().search(domain, limit=1)
            if not client_records:
                _logger.warning("Webhook: no tds.client record found for %s", domain)
                return {'status': 'error', 'message': 'Record not found'}

            client = client_records[0]

            # Create output attachments
            att_ids = []
            existing_ids = client.output_attachment_ids.ids
            for f in output_files:
                att = request.env['ir.attachment'].sudo().create({
                    'name': f['name'],
                    'datas': f['b64'],
                    'res_model': 'tds.client',
                    'res_id': client.id,
                    'description': 'TDS FVU Output (webhook)',
                })
                att_ids.append(att.id)

            # Update the client record
            vals = {
                'state': state if state in ('done', 'failed') else 'done',
                'server_state': state,
                'server_reference': reference,
                'server_validation_id': validation_id or False,
                'execution_log': exec_log,
                'checksum_valid': bool(checksum_valid),
            }
            if att_ids:
                all_ids = existing_ids + att_ids
                vals['output_attachment_ids'] = [(6, 0, all_ids)]
            if error_msg:
                vals['error_message'] = error_msg

            client.sudo().write(vals)

            # Post chatter message
            msg_parts = [
                f"📩 Webhook received from server.",
                f"Reference: {reference}",
                f"State: {state}",
            ]
            if att_ids:
                msg_parts.append(f"📎 {len(att_ids)} file(s) received via webhook.")
            if exec_log:
                msg_parts.append(f"📋 Execution log captured ({len(exec_log.split(chr(10)))} lines).")
            if error_msg:
                msg_parts.append(f"❌ Error: {error_msg}")

            client.sudo().message_post(body=' | '.join(msg_parts))

            _logger.info("Webhook processed for client %s (%s)", client.name, reference)
            return {'status': 'ok', 'message': f'Processed for {client.name}'}

        except Exception as e:
            _logger.exception("Webhook processing error")
            return {'status': 'error', 'message': str(e)}
