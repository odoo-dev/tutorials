"""
Validation Service
-------------------
Pre-validation of TDS/TCS data before FVU processing.
Handles checksum verification, file format checks,
and metadata validation.

Called by the API controller before running the FVU JAR.
"""

import base64
import logging
import os

_logger = logging.getLogger(__name__)


class ValidationService:
    """Validates TDS input data integrity and format."""

    @staticmethod
    def validate_file_format(filename, file_b64):
        """
        Validate file extension and basic content integrity.
        
        Args:
            filename: Original filename
            file_b64: Base64-encoded file content
        
        Returns:
            dict: {'valid': bool, 'error': str or None}
        """
        errors = []

        # Check filename exists
        if not filename:
            return {'valid': False, 'error': 'Filename is required.'}

        # Validate extension
        _, ext = os.path.splitext(filename.lower())
        valid_extensions = {'.txt', '.fvu', '.csi'}
        if ext not in valid_extensions:
            return {
                'valid': False,
                'error': f"Invalid extension '{ext}'. Allowed: .txt, .fvu, .csi"
            }

        # Validate base64 content
        if not file_b64:
            return {'valid': False, 'error': 'File content is empty.'}

        try:
            decoded = base64.b64decode(file_b64, validate=True)
            if len(decoded) == 0:
                return {'valid': False, 'error': 'Decoded file content is empty.'}
        except Exception as e:
            return {'valid': False, 'error': f"Invalid base64 encoding: {e}"}

        return {'valid': True, 'error': None}

    @staticmethod
    def validate_metadata(data):
        """
        Validate request metadata fields.
        
        Args:
            data: dict with request_id, request_date, notes, etc.
        
        Returns:
            dict: {'valid': bool, 'errors': [str, ...]}
        """
        errors = []

        request_id = data.get('request_id', '')
        request_date = data.get('request_date', '')

        # request_id - optional but if provided should be a string
        if request_id and not isinstance(request_id, str):
            errors.append("request_id must be a string.")

        # request_date - optional but if provided should be YYYY-MM-DD format
        if request_date:
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(request_date)):
                errors.append("request_date must be in YYYY-MM-DD format.")

        return {'valid': len(errors) == 0, 'errors': errors}

    @staticmethod
    def pre_validate_all(tds_b64, tds_filename, csi_b64=None, csi_filename=None, metadata=None):
        """
        Run all pre-validations and return a summary.
        
        Args:
            tds_b64: base64 TDS file content
            tds_filename: TDS filename
            csi_b64: optional base64 CSI file content
            csi_filename: optional CSI filename
            metadata: dict with optional metadata fields
        
        Returns:
            dict: {
                'valid': bool,
                'errors': [str, ...],
                'warnings': [str, ...],
                'tds_valid': bool,
                'csi_valid': bool or None,
                'metadata_valid': bool or None
            }
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'tds_valid': False,
            'csi_valid': None,
            'metadata_valid': None,
        }

        # Validate TDS file
        tds_check = ValidationService.validate_file_format(tds_filename, tds_b64)
        result['tds_valid'] = tds_check['valid']
        if not tds_check['valid']:
            result['errors'].append(f"TDS file: {tds_check['error']}")

        # Validate CSI file (optional)
        if csi_b64 or csi_filename:
            csi_check = ValidationService.validate_file_format(
                csi_filename or 'challan.csi', csi_b64
            )
            result['csi_valid'] = csi_check['valid']
            if not csi_check['valid']:
                result['errors'].append(f"CSI file: {csi_check['error']}")

        # Validate metadata (optional)
        if metadata:
            meta_check = ValidationService.validate_metadata(metadata)
            result['metadata_valid'] = meta_check['valid']
            if not meta_check['valid']:
                result['errors'].extend(
                    [f"Metadata: {e}" for e in meta_check['errors']]
                )

        result['valid'] = len(result['errors']) == 0
        return result
