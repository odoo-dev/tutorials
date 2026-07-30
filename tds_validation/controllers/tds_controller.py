import logging

from odoo import http, SUPERUSER_ID
from odoo.http import request

_logger = logging.getLogger(__name__)


class TDSGeneratorController(http.Controller):

    @staticmethod
    def _response(status, message, data=None):
        return {'status': status,
                'message': message,
                'data': data or {}
                }

    @http.route('/api/tds/generate', type='jsonrpc', methods=['POST'], auth='none')
    def generate(self, **kwargs):
        try:
            params = request.params if hasattr(request, 'params') else kwargs
            data = params.get('params') or params
            if isinstance(data, str):
                import json
                data = json.loads(data)

            _logger.info("TDS generate request received")

            # Use admin env so all downstream calls (create, attachment, message_post) work
            env = request.env(user=SUPERUSER_ID)

            checksum = data.get('checksum', '')
            webhook_url = data.get('webhook_url', '')

            TdsValidation = env['tds.validation']
            record = TdsValidation.create({
                'tds_file': data.get('tds_file_b64'),
                'tds_filename': data.get('tds_filename', 'tds.txt'),
                'csi_file': data.get('csi_file_b64', False),
                'csi_filename': data.get('csi_filename', False),
                'db_instance_uuid': data.get('db_instance_uuid', ''),
                'db_name': data.get('db_name', ''),
                'company_name': data.get('company_name', ''),
                'is_api_request': True,
                'request_id': data.get('request_id', ''),
                'checksum': checksum,
                'webhook_url': webhook_url,
                'state': 'draft',
            })

            # Enqueue (checksum validation is synchronous inside)
            record.action_process()

            #  Return immediate 'queued' response 
            return self._response('ok', 'queued', {
                'validation_id': record.id,
                'reference': record.name,
                'state': record.state,
            })

        except Exception as e:
            _logger.exception("TDS generate API error")
            return self._response('error', str(e))
