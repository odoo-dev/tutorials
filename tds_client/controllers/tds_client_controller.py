import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class TDSWebhookController(http.Controller):

    @http.route('/api/tds/webhook', type='jsonrpc', methods=['POST'], auth='public', csrf=False)
    def webhook_receive(self, **kwargs):
        """
        Receive async processing results from the TDS validation server.

        Expected JSON-RPC payload (params):
            validation_id: int
            reference: str
            status: 'ok' | 'error'
            message: str
            output_files: list of {name, b64} (only when status == 'ok')
        """
        try:
            params = request.params if hasattr(request, 'params') else kwargs
            data = params.get('params') or params
            if isinstance(data, str):
                import json
                data = json.loads(data)

            validation_id = data.get('validation_id')
            status = data.get('status', '')
            message = data.get('message', '')
            output_files = data.get('output_files', [])

            _logger.info("Webhook received: validation_id=%s, status=%s", validation_id, status)

            if not validation_id:
                _logger.error("Webhook missing validation_id")
                return {'status': 'ok'}

            env = request.env(user=SUPERUSER_ID)
            TdsClient = env['tds.client']

            # Look up the client record by server_validation_id
            record = TdsClient.search([('server_validation_id', '=', validation_id)], limit=1)

            if not record:
                _logger.warning("No tds.client record found for server_validation_id=%s", validation_id)
                return {'status': 'ok'}

            if status == 'ok':
                # Create output attachments
                att_ids = []
                for f in output_files:
                    att = env['ir.attachment'].create({
                        'name': f['name'],
                        'datas': f['b64'],
                        'res_model': 'tds.client',
                        'res_id': record.id,
                        'description': 'TDS FVU Output — received via webhook',
                    })
                    att_ids.append(att.id)

                record.write({
                    'state': 'done',
                    'output_attachment_ids': [(6, 0, att_ids)],
                    'webhook_received': True,
                    'error_message': False,
                })

                record.message_post(
                    body=f"✅ Webhook received — validation complete. "
                         f"{len(output_files)} output file(s) attached.",
                    subtype_xmlid='mail.mt_note',
                )

            else:
                # status == 'error'
                record.write({
                    'state': 'failed',
                    'error_message': message or 'Unknown server error',
                    'webhook_received': True,
                })

                record.message_post(
                    body=f"❌ Webhook received — validation failed: {message}",
                    subtype_xmlid='mail.mt_note',
                )

            _logger.info("Webhook processed for %s (state=%s)", record.name, record.state)

        except Exception as e:
            _logger.exception("Error processing webhook: %s", e)
            # Always acknowledge to prevent server-side retries

        return {'status': 'ok'}
