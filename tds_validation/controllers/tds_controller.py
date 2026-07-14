"""
TDS API Controller
------------------
REST API endpoints for TDS/TCS file generation, checksum validation,
and FVU processing. Accepts files via POST, validates checksums,
runs the FVU JAR, and returns output.

Endpoints:
  POST /api/tds/generate  — submit .txt + .csi (optional) + checksum + metadata
"""

import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class TDSGeneratorController(http.Controller):

    @http.route('/api/tds/generate', type='jsonrpc', methods=['POST'], auth='user', csrf=False)
    def generate_tds(self, **kwargs):
        """
        POST /api/tds/generate
        {
            "tds_file_b64": "base64...",        # required
            "tds_filename": "tds.txt",           # required
            "csi_file_b64": "base64...",         # optional
            "csi_filename": "challan.csi",       # optional
            "checksum": "sha256hex...",          # optional (if provided, validated)
            "request_id": "REQ-001",             # optional - external reference
            "request_date": "2026-07-13",        # optional
            "notes": "any notes"                 # optional
        }
        Returns:
        {
            "status": "ok"/"error",
            "message": "...",
            "data": {
                "validation_id": 123,
                "reference": "TDS/2026/0001",
                "output_files": [{"name": "...", "b64": "..."}],
                "checksum_valid": true/false
            }
        }
        """
        try:
            # ── 1. Parse input ──────────────────────────────────────────
            params = request.params if hasattr(request, 'params') else kwargs
            data = params.get('params') or params
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    data = params

            _logger.info("TDS generate request received: %s", data.get('request_id', 'N/A'))

            tds_b64 = data.get('tds_file_b64', '')
            tds_filename = data.get('tds_filename', 'tds.txt')
            csi_b64 = data.get('csi_file_b64')
            csi_filename = data.get('csi_filename')
            checksum_input = data.get('checksum', '')
            request_id = data.get('request_id', '')
            request_date = data.get('request_date', '')
            notes = data.get('notes', '')

            # ── 2. Validate required fields ─────────────────────────────
            errors = []
            if not tds_b64:
                errors.append("tds_file_b64 is required.")
            if not tds_filename:
                errors.append("tds_filename is required.")

            if tds_filename and not (tds_filename.lower().endswith('.txt') or tds_filename.lower().endswith('.fvu')):
                errors.append("tds_filename must end with .txt or .fvu")
            if csi_filename and not csi_filename.lower().endswith('.csi'):
                errors.append("csi_filename must end with .csi")

            if errors:
                return self._response('error', '; '.join(errors))

            # ── 3. Checksum validation (if provided) ────────────────────
            checksum_valid = None
            computed_checksum = ''
            if checksum_input:
                checksum_valid = self._validate_checksum(
                    tds_b64, csi_b64, checksum_input
                )
                if not checksum_valid:
                    try:
                        from ..services.checksum_generator import ChecksumGenerator
                        computed_checksum = ChecksumGenerator.generate(tds_b64, csi_b64)
                    except Exception:
                        computed_checksum = ''
                    _logger.warning(
                        'Checksum mismatch — provided: %s, computed: %s',
                        checksum_input, computed_checksum
                    )

            # ── 4. Create tds.validation record ─────────────────────────
            TdsValidation = request.env['tds.validation']
            vals = {
                'tds_file': tds_b64,
                'tds_filename': tds_filename,
                'consolidate_file': csi_b64 or False,
                'consolidate_filename': csi_filename or False,
                'checksum': checksum_input or False,
                'checksum_valid': bool(checksum_valid) if checksum_valid is not None else False,
                'request_id': request_id or False,
                'request_date': request_date or False,
                'notes': notes or False,
                'is_api_request': True,
                'state': 'draft',
            }
            validation = TdsValidation.create(vals)

            # ── 5. Run validation (FVU JAR) ────────────────────────────
            try:
                validation.action_run_validation()
            except Exception as run_e:
                _logger.exception("FVU run failed for validation %s", validation.id)
                # validation state is already 'failed' with error_message set
                pass

            # ── 6. Collect output ──────────────────────────────────────
            output_files = []
            if validation.state == 'done':
                for att in validation.output_attachment_ids:
                    output_files.append({
                        'name': att.name,
                        'b64': att.datas.decode() if att.datas else '',
                    })

            # ── 7. Collect execution log ───────────────────────────────
            execution_log = validation.execution_log or ''

            response_data = {
                'validation_id': validation.id,
                'reference': validation.name,
                'state': validation.state,
                'output_files': output_files,
                'error_message': validation.error_message or '',
                'execution_log': execution_log,
            }
            if checksum_input:
                response_data['checksum_valid'] = bool(checksum_valid)
                if not checksum_valid:
                    response_data['computed_checksum'] = computed_checksum if computed_checksum else ''
                    response_data['warning'] = 'Checksum mismatch — data processed anyway.'
            else:
                response_data['checksum_valid'] = None

            return self._response('ok', 'TDS validation processed.', response_data)

        except Exception as e:
            _logger.exception("TDS generate API error")
            return self._response('error', str(e))

    def _validate_checksum(self, tds_b64, csi_b64, input_checksum):
        """Validate SHA-256 checksum of the input files."""
        try:
            from ..services.checksum_generator import ChecksumGenerator
            validator = ChecksumGenerator()
            return validator.validate(tds_b64, csi_b64, input_checksum)
        except ImportError:
            _logger.warning("ChecksumGenerator not available, skipping validation")
            return True
        except Exception as e:
            _logger.warning("Checksum validation error: %s", e)
            return False

    @staticmethod
    def _response(status, message, data=None):
        """Build standardized JSON response."""
        result = {'status': status, 'message': message}
        if data:
            result['data'] = data
        return result
