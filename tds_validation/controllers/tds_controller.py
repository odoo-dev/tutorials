import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TDSGeneratorController(http.Controller):

    @http.route('/api/tds/generate', type='jsonrpc', methods=['POST'], auth='public', csrf=False)
    def generate_tds(self, **kwargs):
        try:
            params = request.params if hasattr(request, 'params') else kwargs
            data = params.get('params') or params
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    data = params
            tds_file_b64 = data.get('tds_file_b64', '')
            tds_filename = data.get('tds_filename', '')
            csi_file_b64 = data.get('csi_file_b64', '')
            csi_filename = data.get('csi_filename', '')
            # Client metadata
            db_instance_uuid = data.get('db_instance_uuid', '')
            db_name = data.get('db_name', '')
            company_name = data.get('company_name', '')

            # validation required fields
            if not tds_file_b64:
                return self._response('error', 'tds_file_b64 is required.')
            if not tds_filename:
                return self._response('error', 'tds_filename is required.')
            # CSI file is optional — only validate if one of the two fields was sent
            if (csi_file_b64 and not csi_filename):
                return self._response('error', 'csi_filename is required when csi_file_b64 is provided.')
            if (csi_filename and not csi_file_b64):
                return self._response('error', 'csi_file_b64 is required when csi_filename is provided.')

            # create tds.validation record
            validation = request.env['tds.validation'].create({
                'tds_file': tds_file_b64,
                'tds_filename': tds_filename,
                'csi_file': csi_file_b64,
                'csi_filename': csi_filename,
                'db_instance_uuid': db_instance_uuid,
                'db_name': db_name,
                'company_name': company_name,
                'state': 'draft',
            })

            validation.action_process()

            # Collect output files
            output_files = []
            for att in validation.output_attachment_ids:
                output_files.append({
                    'name': att.name,
                    'b64': att.datas.decode() if att.datas else '',
                })

            #  Return success
            return self._response('ok', 'processed', {
                'validation_id': validation.id,
                'reference': validation.name,
                'output_files': output_files,
            })
        except Exception as e:
            _logger.exception('TDS generate API error')
            return self._response('error', str(e))

    # Helper Methods
    @staticmethod
    def _response(status, message, data=None):
        result = {'status': status, 'message': message}
        if data:
            result['data'] = data
        return result
