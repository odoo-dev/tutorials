import base64
import logging
import os
import subprocess
import tempfile
import time

_logger = logging.getLogger(__name__)

OUTPUT_TIMEOUT = 180  # seconds
DISPLAY_START = 200


class FVURunner:

    def __init__(self, record_id, jar_dir):
        self.record_id = record_id
        self.jar_dir = jar_dir

        self.tmp_dir = None
        self.output_dir = None
        self.xvfb_proc = None
        self.display = None
        self.jar_proc = None
        self.jar_file = None

        # ── Validate JAR directory ──────────────────────────────
        if not os.path.isdir(jar_dir):
            raise FileNotFoundError(
                f"FVU JAR directory not found: {jar_dir}"
            )

        # ── Find FVU JAR ────────────────────────────────────────
        # No version extraction/checking.
        candidates = [
            fname
            for fname in os.listdir(jar_dir)
            if fname.endswith('.jar')
               and 'TDS_STANDALONE_FVU' in fname
        ]

        if not candidates:
            raise FileNotFoundError(
                f"No TDS_STANDALONE_FVU JAR found in {jar_dir}"
            )

        # Deterministic selection if more than one matching JAR exists.
        candidates.sort()
        self.jar_file = candidates[0]

        _logger.info(
            "FVURunner initialized — JAR: %s",
            self.jar_file,
        )

    def run(self, tds_b64, tds_filename, csi_b64=None, csi_filename=None):
        self._create_temp_dir()
        tds_input_path = self._write_file(tds_filename or 'tds.txt', tds_b64)
        _logger.info("TDS input written: %s (%d bytes)", tds_input_path, os.path.getsize(tds_input_path))

        csi_input_path = ''
        if csi_b64:
            csi_input_path = self._write_file(csi_filename or 'challen.csi', csi_b64)
            _logger.info("CSI input written: %s (%d bytes)", csi_input_path,
                         os.path.getsize(csi_input_path))

        else:
            _logger.info("No CSI file provided -- JAR called without it.")
        self._start_xvfb()

    def _create_temp_dir(self):
        """Create a fresh temporary directory with an output/ subfolder."""
        self.tmp_dir = tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')
        self.output_dir = os.path.join(self.tmp_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)
        _logger.info("Temp dir create : %s", self.tmp_dir)

    @staticmethod
    def _write_file(path, b64_date):
        """Decode base64 data and write to the given path."""
        full_path = os.path.abspath(path)
        with open(full_path, 'wb') as fh:
            fh.write(base64.b16decode(b64_date))
        return full_path

    @staticmethod
    def _find_free_display():
        n = DISPLAY_START
        while os.path.exists(f'/tmp/.X{n}-lock'):
            n += 1
        return n

    def _start_xvfb(self):
        n = self._find_free_display()
        self.display = f':{n}'
        self.xvfb_proc = subprocess.Popen(
            ['Xvfb', self.display, '-screen', '0', '1280x800x24'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)  # Allow Xvfb to initialise
        _logger.info("Xvfb started on display %s (PID %s)",
                     self.display, self.xvfb_proc.pid)
