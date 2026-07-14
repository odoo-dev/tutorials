"""
FVU Version Checker Service
----------------------------
Mirrors the version check logic from test.sh:
  1. Auto-detect FVU version from JAR filename
  2. POST to TIN server (proteantech.in)
  3. Compare versions — MAJOR mismatch blocks, MINOR outdated warns

Config:
  - JAR_DIR from ir.config_parameter 'tds_validation.jar_dir'
  - Server URL from VersionValidator.jar (proteantech.in)
"""

import logging
import os
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

_logger = logging.getLogger(__name__)

DEMO_MODE = os.environ.get('TDS_DEMO_MODE', '0') == '1'

VERSION_URL = 'https://onlineservices.tin.egov.proteantech.in/TIN/checkfvuversion.do'
TIMEOUT = 15


def get_local_version(jar_dir):
    """
    Auto-detect FVU version from JAR filename in jar_dir.
    Returns (version_string, error_message_or_None).
    """
    if not os.path.isdir(jar_dir):
        return None, f"FVU JAR directory not found: {jar_dir}"

    for f in sorted(os.listdir(jar_dir), reverse=True):
        m = re.search(r'FVU_([0-9]+\.[0-9]+)', f)
        if m and f.endswith('.jar'):
            return m.group(1), None

    return None, (
        f"No TDS_STANDALONE_FVU_*.jar found in {jar_dir}\n"
        f"Please place the FVU JAR file in: {jar_dir}"
    )


class FVUVersionChecker:
    """Checks FVU version against TIN server. Blocks on major mismatch."""

    def __init__(self, jar_dir):
        self.jar_dir = jar_dir

    def check(self):
        """Returns dict with status, local_version, server_version, message, can_proceed."""

        # ── Demo mode: skip real version check ──
        if DEMO_MODE:
            _logger.info("DEMO MODE — skipping version check against TIN server")
            return {
                'status': 'current',
                'local_version': '9.9 (demo)',
                'server_version': '9.9 (demo)',
                'message': 'DEMO MODE — version check skipped. Proceeding with validation.',
                'can_proceed': True,
            }

        local_version, jar_error = self._detect()
        if jar_error:
            return {
                'status': 'error',
                'local_version': None,
                'server_version': None,
                'message': jar_error,
                'can_proceed': False,
            }

        _logger.info("Local FVU version  : %s", local_version)

        server_raw = self._fetch_version()
        if not server_raw:
            return {
                'status': 'error',
                'local_version': local_version,
                'server_version': None,
                'message': (
                    'TIN VERSION CHECK SERVER UNREACHABLE!\n'
                    'Cannot verify FVU version. Validation ABORTED.\n'
                    'Check internet connection.'
                ),
                'can_proceed': False,
            }

        server_version = server_raw.strip().split('^')[0] if server_raw.strip() else ''
        _logger.info("Server latest FVU   : %s", server_version)

        if not server_version:
            return {
                'status': 'error',
                'local_version': local_version,
                'server_version': None,
                'message': f'Server returned empty version. Raw: {server_raw}. ABORTED.',
                'can_proceed': False,
            }

        return self._compare(local_version, server_version)

    def _detect(self):
        return get_local_version(self.jar_dir)

    def _fetch_version(self):
        try:
            resp = requests.post(
                VERSION_URL,
                data={'fvu_version': '1'},
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Language': 'en-US',
                },
                verify=False,
                timeout=TIMEOUT,
            )
            resp.raise_for_status()
            text = resp.text.strip()
            _logger.info("Server response: %s", text)
            return text
        except Exception as e:
            _logger.warning("Version check failed: %s", e)
            return None

    def _compare(self, local_version, server_version):
        l_maj, l_min = self._parse(local_version)
        s_maj, s_min = self._parse(server_version)

        if l_maj is None or s_maj is None:
            if local_version == server_version:
                return self._ok(local_version, server_version)
            return self._major_block(local_version, server_version)

        if l_maj != s_maj:
            return self._major_block(local_version, server_version)

        if l_min < s_min:
            return {
                'status': 'warn',
                'local_version': local_version,
                'server_version': server_version,
                'message': (
                    f'Minor version outdated (yours: {local_version}, '
                    f'latest: {server_version}).\n'
                    f'Continuing — minor updates are not blocking.'
                ),
                'can_proceed': True,
            }

        return self._ok(local_version, server_version)

    @staticmethod
    def _major_block(local_version, server_version):
        return {
            'status': 'old',
            'local_version': local_version,
            'server_version': server_version,
            'message': (
                f'FVU MAJOR VERSION MISMATCH!\n'
                f'Your version: {local_version}, Latest: {server_version}\n'
                f'Download latest FVU from TIN website.\n'
                f'Validation ABORTED.'
            ),
            'can_proceed': False,
        }

    @staticmethod
    def _ok(local_version, server_version):
        return {
            'status': 'current',
            'local_version': local_version,
            'server_version': server_version,
            'message': f'FVU version is UP-TO-DATE ({local_version}).',
            'can_proceed': True,
        }

    @staticmethod
    def _parse(v):
        try:
            parts = v.split('.')
            return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
        except (ValueError, TypeError, IndexError):
            return None, None
