"""
Checksum Generator Service
---------------------------
SHA-256 checksum generation and validation for TDS/TCS files.
Used by the API controller to verify data integrity.

Functions:
  - generate_checksum(tds_b64, csi_b64=None) → str
  - validate(tds_b64, csi_b64, expected_checksum) → bool
"""

import base64
import hashlib
import logging

_logger = logging.getLogger(__name__)


class ChecksumGenerator:
    """Generates and validates SHA-256 checksums for TDS input files."""

    @staticmethod
    def generate(tds_b64, csi_b64=None):
        """
        Generate SHA-256 checksum from base64-encoded file content.
        
        Args:
            tds_b64: base64 string of the .txt/.fvu file (required)
            csi_b64: base64 string of the .csi file (optional)
        
        Returns:
            Hex-encoded SHA-256 hash string
        """
        sha = hashlib.sha256()

        # Hash TDS file content - decode base64 to get raw bytes
        try:
            tds_raw = base64.b64decode(tds_b64)
            sha.update(tds_raw)
        except Exception as e:
            _logger.warning("Could not decode tds_b64 for checksum: %s", e)
            sha.update(tds_b64.encode('utf-8'))

        # Optionally include CSI file in hash
        if csi_b64:
            try:
                csi_raw = base64.b64decode(csi_b64)
                sha.update(csi_raw)
            except Exception as e:
                _logger.warning("Could not decode csi_b64 for checksum: %s", e)
                sha.update(csi_b64.encode('utf-8'))

        checksum = sha.hexdigest()
        _logger.info("Generated checksum: %s", checksum)
        return checksum

    @staticmethod
    def validate(tds_b64, csi_b64, expected_checksum):
        """
        Validate that the generated checksum matches the expected value.
        
        Args:
            tds_b64: base64 string of the .txt/.fvu file
            csi_b64: base64 string of the .csi file (optional)
            expected_checksum: hex-encoded SHA-256 hash to compare against
        
        Returns:
            bool: True if checksums match
        """
        computed = ChecksumGenerator.generate(tds_b64, csi_b64)
        is_valid = computed.lower() == expected_checksum.lower()

        if is_valid:
            _logger.info("Checksum validation PASSED")
        else:
            _logger.warning(
                "Checksum validation FAILED — computed: %s, expected: %s",
                computed, expected_checksum
            )

        return is_valid
