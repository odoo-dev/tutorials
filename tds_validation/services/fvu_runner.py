"""
FVU Runner Service
------------------
Runs TDS FVU JAR in CLI mode with Xvfb + file-polling.
The stale GIO module cache from the VS Code Snap runtime is
bypassed via GIO_MODULE_DIR, which eliminates the GLib crash.
"""

import base64
import logging
import os
import shutil
import subprocess
import tempfile
import time

_logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
JAR_DIR = '/home/odoo/Downloads/TDS_STANDALONE_FVU_1.0'
JAR_FILE = 'TDS_STANDALONE_FVU_1.0.jar'
JAR_VERSION = '1.0'


class FVURunner:
    """
    One instance per validation run.
    Mirrors run_fvu_cli.sh: Xvfb + background JAR + file-polling.
    """

    def __init__(self, record_id):
        self.record_id = record_id
        self.tmp_dir = None
        self.output_dir = None
        self.xvfb_pid = None
        self.display = None
        self.jar_pid = None
        self.proc = None

    # ── Public ────────────────────────────────────────────────────────────────

    def run(self, tds_b64, tds_filename, challan_b64, challan_filename,
            consolidate_b64=None, consolidate_filename=None):
        try:
            self._create_temp_dir()
            tds_path = self._write_file(tds_filename or 'tds.txt', tds_b64)
            challan_path = self._write_file(challan_filename or 'challan.csi', challan_b64)
            consolidate_path = ''
            if consolidate_b64:
                consolidate_path = self._write_file(
                    consolidate_filename or 'consolidate.txt', consolidate_b64)

            err_path = os.path.join(self.tmp_dir, 'err.err')

            self._start_xvfb()
            self._launch_jar(tds_path, err_path, self.output_dir, consolidate_path)
            self._wait_for_output()

            return self._collect_outputs()

        except Exception as e:
            _logger.error("Validation failed: %s", e)
            raise

        finally:
            self._cleanup()

    def cleanup(self):
        self._cleanup()
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)
            _logger.info("Cleaned up: %s", self.tmp_dir)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _create_temp_dir(self):
        self.tmp_dir = tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')
        self.output_dir = os.path.join(self.tmp_dir, 'output')
        os.makedirs(self.output_dir)
        _logger.info("Temp dir: %s", self.tmp_dir)

    def _write_file(self, filename, b64_data):
        path = os.path.join(self.tmp_dir, filename)
        with open(path, 'wb') as f:
            f.write(base64.b64decode(b64_data))
        _logger.info("Wrote: %s", path)
        return path

    def _find_free_display(self):
        num = 200
        while os.path.exists(f'/tmp/.X{num}-lock'):
            num += 1
        return num

    def _start_xvfb(self):
        num = self._find_free_display()
        self.display = f':{num}'
        proc = subprocess.Popen(
            ['Xvfb', self.display, '-screen', '0', '1280x800x24'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.xvfb_pid = proc.pid
        time.sleep(1)
        _logger.info("Xvfb started on %s (PID %d)", self.display, self.xvfb_pid)

    def _build_env(self):
        """Clean env — bypass stale Snap GIO cache via GIO_MODULE_DIR."""
        env = {}
        for v in ('HOME', 'USER', 'LANG'):
            if v in os.environ:
                env[v] = os.environ[v]
        env['DISPLAY'] = self.display
        env['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        # GIO_MODULE_DIR points at an empty directory to prevent GLib
        # from loading stale cached plugins from the Snap runtime.
        env['GIO_MODULE_DIR'] = os.path.join(self.tmp_dir, 'gio-empty')
        os.makedirs(env['GIO_MODULE_DIR'], exist_ok=True)
        env['GTK_MODULES'] = ''
        env['NO_AT_BRIDGE'] = '1'
        env['GDK_BACKEND'] = 'x11'
        return env

    def _launch_jar(self, tds_path, err_path, output_dir, consolidate_path=''):
        jar_path = os.path.join(JAR_DIR, JAR_FILE)
        if not os.path.isfile(jar_path):
            raise FileNotFoundError(f"JAR not found: {jar_path}")

        env = self._build_env()

        jvm_args = [
            '-Xmx512m',
            '-XX:CompressedClassSpaceSize=256m',
            '-XX:MaxMetaspaceSize=256m',
        ]

        cmd = (
            ['java'] + jvm_args + ['-jar', jar_path]
            + [tds_path, err_path, output_dir + '/', '0', JAR_VERSION, '1']
            + ([consolidate_path] if consolidate_path else [''])
        )

        _logger.info("Launching JAR (Xvfb): %s", ' '.join(cmd))

        self.proc = subprocess.Popen(
            cmd,
            cwd=JAR_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.jar_pid = self.proc.pid
        _logger.info("JAR PID: %d", self.jar_pid)

    def _wait_for_output(self, timeout=180):
        """
        Poll for output files — mirrors the bash script's while-true loop.
        Detects completion when:
        - 'tds.err' AND 'tdserr.html' exist in JAR_DIR (error)
        - Any file appears in output_dir (success)
        """
        _logger.info("Polling for output files (timeout=%ds)...", timeout)
        start = time.time()

        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                _logger.warning("Timeout (%ds) reached — no output files detected", timeout)
                return

            # Error files generated in JAR_DIR
            tds_err = os.path.join(JAR_DIR, 'tds.err')
            tds_err_html = os.path.join(JAR_DIR, 'tdserr.html')
            if os.path.isfile(tds_err) and os.path.isfile(tds_err_html):
                _logger.info("Validation completed (Error report generated).")
                return

            # Success: any file in output_dir
            if os.path.isdir(self.output_dir):
                files = [f for f in os.listdir(self.output_dir)
                         if os.path.isfile(os.path.join(self.output_dir, f))]
                if files:
                    _logger.info("Validation completed (Output generated): %s", files)
                    return

            time.sleep(1)

    def _cleanup(self):
        """Kill JAR first, then Xvfb — mirrors bash trap cleanup."""
        if self.jar_pid:
            try:
                os.kill(self.jar_pid, 15)
                _logger.info("JAR (PID %d) stopped", self.jar_pid)
            except ProcessLookupError:
                pass
            self.jar_pid = None

        if self.proc and self.proc.stdout:
            try:
                out, err = self.proc.communicate(timeout=5)
                if out and out.strip():
                    _logger.info("JAR remainder stdout: %s", out.decode(errors='ignore')[:300])
                if err and err.strip():
                    _logger.info("JAR remainder stderr: %s", err.decode(errors='ignore')[:300])
            except Exception:
                pass

        try:
            subprocess.run(['pkill', '-f', JAR_FILE],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        if self.xvfb_pid:
            try:
                os.kill(self.xvfb_pid, 9)
                _logger.info("Xvfb %s stopped", self.display)
            except ProcessLookupError:
                pass
            self.xvfb_pid = None

    def _collect_outputs(self):
        """
        Collect output files from:
        - output_dir (success .fvu files)
        - tmp_dir root for .err/.html/.fvu
        - JAR_DIR error files (tds.err, tdserr.html) — per bash script logic
        """
        results = []

        # 1. Output dir files (success case)
        if os.path.isdir(self.output_dir):
            for fname in os.listdir(self.output_dir):
                fpath = os.path.join(self.output_dir, fname)
                if os.path.isfile(fpath):
                    results.append(self._read_file(fpath))

        # 2. Error files from JAR_DIR (matching bash script)
        for fname in ('tds.err', 'tdserr.html'):
            fpath = os.path.join(JAR_DIR, fname)
            if os.path.isfile(fpath):
                results.append(self._read_file(fpath))
                try:
                    shutil.move(fpath, os.path.join(self.tmp_dir, fname + '.bak'))
                except Exception:
                    pass

        # 3. Other .err/.html/.fvu files in tmp_dir root
        for fname in os.listdir(self.tmp_dir):
            fpath = os.path.join(self.tmp_dir, fname)
            if os.path.isfile(fpath) and fname.endswith(('.err', '.html', '.fvu')):
                if fname not in ('tds.txt', 'challan.csi', 'consolidate.txt', 'err.err'):
                    results.append(self._read_file(fpath))

        _logger.info("Collected %d output files", len(results))
        return results

    def _read_file(self, path):
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        return {'name': os.path.basename(path), 'b64': data}
