"""
FVU Runner Service
------------------
Runs TDS FVU JAR in CLI mode with Xvfb + file-polling.
Auto-detects JAR file and version from the configured JAR_DIR.
Kills Java immediately when output files appear to prevent popups.

Supports DEMO_MODE for happy-flow testing without the real JAR.

Production features:
  - Accepts jar_dir as parameter (from ir.config_parameter)
  - JVM heap limits to prevent OOM
  - Clean env to avoid Snap GLib crashes
  - Orphan temp dir cleanup on init
"""

import base64
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time

_logger = logging.getLogger(__name__)

OUTPUT_TIMEOUT = 180  # seconds

# ── Demo mode ────────────────────────────────────────────────────────────────
# When DEMO_MODE is True, the runner creates fake output files instead of
# running the real FVU JAR. This is useful for testing the full pipeline
# end-to-end without the actual government FVU utility.
# Enable via config parameter 'tds_validation.demo_mode' = 'True'
# or by setting the env var TDS_DEMO_MODE=1
DEMO_MODE = os.environ.get('TDS_DEMO_MODE', '0') == '1'
DEMO_DELAY = 5  # seconds to simulate processing time


def _detect_jar_info(jar_dir):
    """Return (jar_filename, jar_version) or raise FileNotFoundError."""
    if not os.path.isdir(jar_dir):
        raise FileNotFoundError(f"JAR_DIR not found: {jar_dir}")

    for f in sorted(os.listdir(jar_dir), reverse=True):
        if f.endswith('.jar') and 'TDS_STANDALONE_FVU' in f:
            m = re.search(r'FVU_([0-9]+\.[0-9]+)', f)
            return f, m.group(1) if m else '1.0'

    raise FileNotFoundError(
        f"No TDS_STANDALONE_FVU_*.jar found in {jar_dir}\n"
        f"Expected filename pattern: TDS_STANDALONE_FVU_<version>.jar"
    )


def _clean_orphan_temps(prefix='tds_', max_age_hours=24):
    """Remove temp dirs left by crashed runs."""
    tmp_root = tempfile.gettempdir()
    now = time.time()
    cleaned = 0
    for entry in os.listdir(tmp_root):
        path = os.path.join(tmp_root, entry)
        if os.path.isdir(path) and entry.startswith(prefix):
            try:
                age = now - os.path.getctime(path)
                if age > max_age_hours * 3600:
                    shutil.rmtree(path, ignore_errors=True)
                    cleaned += 1
            except (OSError, ValueError):
                pass
    if cleaned:
        _logger.info("Cleaned %d orphan temp dirs (prefix=%s, age>%dh)",
                     cleaned, prefix, max_age_hours)


class FVURunner:
    """One instance per validation run."""

    def __init__(self, record_id, jar_dir, elog=None):
        self.record_id = record_id
        self.jar_dir = jar_dir
        self.elog = elog
        self.tmp_dir = None
        self.output_dir = None
        self.xvfb_pid = None
        self.display = None
        self.jar_pid = None
        self.proc = None

        _clean_orphan_temps()

        self.demo_mode = DEMO_MODE
        if not self.demo_mode:
            self.jar_file, self.jar_version = _detect_jar_info(jar_dir)
            _logger.info("Using JAR: %s (version: %s)", self.jar_file, self.jar_version)
        else:
            self.jar_file = 'DEMO_MODE'
            self.jar_version = '9.9'
            _logger.info("DEMO MODE — no JAR required. Fake output will be generated.")

    # ── Log helper ─────────────────────────────────────────────────────

    def _log(self):
        """Access the ExecutionLogger (maybe None)."""
        return self.elog

    # ── Public ────────────────────────────────────────────────────────────────

    def run(self, tds_b64, tds_filename,
            consolidate_b64=None, consolidate_filename=None):
        """
        Args:
            tds_b64: base64-encoded TDS input file
            tds_filename: original filename
            consolidate_b64: optional base64-encoded consolidate file
            consolidate_filename: optional filename

        Returns: list of {'name': str, 'b64': str} output files
        """
        try:
            elog = self._log()

            if self.demo_mode:
                return self._run_demo(tds_b64, tds_filename, consolidate_b64, consolidate_filename)

            if elog:
                elog.section('FVU Runner — Setup')

            self._create_temp_dir()

            tds_path = self._write_file(tds_filename or 'tds.txt', tds_b64)
            if elog:
                elog.ok(f"TDS input file written: {os.path.basename(tds_path)}")
                elog.detail('Input size', f"{os.path.getsize(tds_path):,} bytes")

            consolidate_path = ''
            if consolidate_b64:
                consolidate_path = self._write_file(
                    consolidate_filename or 'consolidate.csi', consolidate_b64)
                if elog:
                    elog.ok(f"CSI file written: {os.path.basename(consolidate_path)}")
            else:
                if elog:
                    elog.info('No consolidate file — proceeding without it')

            input_base = os.path.splitext(os.path.basename(tds_path))[0]
            err_path = os.path.join(self.output_dir, f"{input_base}.err")

            if elog:
                elog.detail('Error output path', err_path)
                elog.detail('Output directory', self.output_dir)

            _logger.info(
                "TDS: %s, Err: %s, Out: %s, Cons: %s",
                tds_path, err_path, self.output_dir,
                consolidate_path or '(none)',
            )

            if elog:
                elog.section('FVU Runner — Xvfb + JAR')

            self._start_xvfb()
            self._launch_jar(tds_path, err_path, self.output_dir, consolidate_path)
            self._wait_for_output()

            return self._collect_outputs()

        except Exception as e:
            _logger.error("Validation failed [rec %s]: %s", self.record_id, e)
            raise

        finally:
            self._cleanup()

    def _run_demo(self, tds_b64, tds_filename,
                  consolidate_b64=None, consolidate_filename=None):
        """
        Demo mode — simulates a successful FVU validation without the real JAR.
        Creates fake output files after a short delay.
        """
        elog = self._log()

        if elog:
            elog.section('DEMO MODE — Simulating FVU Validation')
            elog.info('Demo mode is ACTIVE — no real JAR will be launched.')
            elog.ok(f'Input file: {tds_filename} ({len(tds_b64):,} bytes base64)')
            if consolidate_b64:
                elog.ok(f'Consolidate file: {consolidate_filename} ({len(consolidate_b64):,} bytes base64)')
            else:
                elog.info('No consolidate file provided')

        self._create_temp_dir()

        # Simulate processing time
        fname_stem = os.path.splitext(tds_filename or 'TDS')[0]
        if elog:
            elog.info(f'Simulating FVU processing ({DEMO_DELAY}s delay)...')

        for i in range(DEMO_DELAY):
            time.sleep(1)
            if elog:
                elog.detail(f'  Processing...', f'{i+1}/{DEMO_DELAY}s')

        if elog:
            elog.ok('FVU processing complete')

        # Create fake output files
        output_files = []

        # 1. Main FVU output file
        fvu_name = f"{fname_stem}_FVU_{self.record_id}.fvu"
        fvu_path = os.path.join(self.output_dir, fvu_name)
        fvu_content = f"""FVU Demo Output
================
Record ID: {self.record_id}
Input File: {tds_filename}
Validation Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Status: SUCCESS
Remarks: This is a DEMO output file — no real FVU validation was performed.

Summary:
  Total Deductees: 42
  Total Amount: 1,234,567.89
  Challan Count: 3
"""
        with open(fvu_path, 'w') as f:
            f.write(fvu_content)
        output_files.append(fvu_path)

        # 2. Summary report
        rpt_name = f"{fname_stem}_Summary.rpt"
        rpt_path = os.path.join(self.output_dir, rpt_name)
        rpt_content = f"""TDS FVU Summary Report (DEMO)
===================================
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
File: {tds_filename}

Deductee Details:
  - PAN: ABCDE1234F | Amount: 1,23,456 | TDS: 12,345
  - PAN: FGHIJ5678K | Amount: 2,34,567 | TDS: 23,456
  - PAN: KLMNO9012P | Amount: 3,45,678 | TDS: 34,567

Total Deductees: 3
Total TDS Amount: 70,368

Challan Details:
  - BSR Code: 123456 | Date: 2026-04-15 | Amount: 25,000
  - BSR Code: 123456 | Date: 2026-06-15 | Amount: 25,368

This is a DEMO report for testing purposes only.
"""
        with open(rpt_path, 'w') as f:
            f.write(rpt_content)
        output_files.append(rpt_path)

        if elog:
            elog.ok(f'Created {len(output_files)} demo output file(s)')
            for fp in output_files:
                elog.detail(f'  📄 {os.path.basename(fp)}', f'{os.path.getsize(fp):,} bytes')

        results = [self._read_file(fp) for fp in output_files]
        return results

    def cleanup(self):
        """Public cleanup — kills processes and removes temp directory."""
        elog = self._log()
        if not self.demo_mode:
            self._cleanup()
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)
            msg = f"Cleaned up temp directory: {self.tmp_dir}"
            _logger.info(msg)
            if elog:
                elog.ok(msg)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _create_temp_dir(self):
        self.tmp_dir = tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')
        self.output_dir = os.path.join(self.tmp_dir, 'output')
        os.makedirs(self.output_dir)
        elog = self._log()
        if elog:
            elog.detail('Temp directory', self.tmp_dir)
            elog.detail('Output subdirectory', self.output_dir)

    @staticmethod
    def _write_file(path, b64_data):
        with open(path, 'wb') as f:
            f.write(base64.b64decode(b64_data))
        return path

    @staticmethod
    def _find_free_display():
        n = 200
        while os.path.exists(f'/tmp/.X{n}-lock'):
            n += 1
        return n

    def _start_xvfb(self):
        n = self._find_free_display()
        self.display = f':{n}'
        proc = subprocess.Popen(
            ['Xvfb', self.display, '-screen', '0', '1280x800x24'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.xvfb_pid = proc.pid
        time.sleep(1)
        msg = f"Xvfb started on display {self.display} (PID {self.xvfb_pid})"
        _logger.info(msg)
        elog = self._log()
        if elog:
            elog.ok(msg)

    def _build_env(self):
        env = {}
        for v in ('HOME', 'USER', 'LANG'):
            if v in os.environ:
                env[v] = os.environ[v]
        env['DISPLAY'] = self.display
        env['PATH'] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        gio_dir = os.path.join(self.tmp_dir, 'gio-empty')
        env['GIO_MODULE_DIR'] = gio_dir
        os.makedirs(gio_dir, exist_ok=True)
        env['GTK_MODULES'] = ''
        env['NO_AT_BRIDGE'] = '1'
        env['GDK_BACKEND'] = 'x11'

        elog = self._log()
        if elog:
            elog.detail('Clean env built', f'DISPLAY={self.display}, GIO_MODULE_DIR={gio_dir}')

        return env

    def _launch_jar(self, tds_path, err_path, output_dir, consolidate_path=''):
        jar_path = os.path.join(self.jar_dir, self.jar_file)
        if not os.path.isfile(jar_path):
            raise FileNotFoundError(f"JAR not found: {jar_path}")

        env = self._build_env()
        args = [
            tds_path, err_path, output_dir + '/',
            '0', self.jar_version, '1',
            consolidate_path or '',
        ]
        cmd = ['java',
               '-Xmx512m',
               '-XX:CompressedClassSpaceSize=256m',
               '-XX:MaxMetaspaceSize=256m',
               '-jar', jar_path] + args

        jar_cmd_str = ' '.join(cmd)
        _logger.info("Launching JAR: %s", jar_cmd_str)

        elog = self._log()
        if elog:
            elog.info(f"Launching Java/FVU...")
            elog.detail('JAR', self.jar_file)
            elog.detail('JVM args', '-Xmx512m -XX:CompressedClassSpaceSize=256m -XX:MaxMetaspaceSize=256m')

        self.proc = subprocess.Popen(
            cmd, cwd=self.jar_dir, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.jar_pid = self.proc.pid
        msg = f"JAR launched (PID {self.jar_pid})"
        _logger.info(msg)
        if elog:
            elog.ok(msg)

    def _wait_for_output(self, timeout=OUTPUT_TIMEOUT):
        _logger.info("Polling for output (timeout=%ds)...", timeout)
        elog = self._log()
        if elog:
            elog.info(f"Polling for output files (timeout={timeout}s)...")

        start = time.time()

        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                _logger.warning("Timeout — killing JAR.")
                if elog:
                    elog.error(f"Timeout ({timeout}s) — no output detected. Killing JAR.")
                self._kill_jar()
                raise TimeoutError(
                    f"FVU did not produce output within {timeout}s. "
                    f"The JAR may be stuck on a popup or the input file may be invalid."
                )

            if os.path.isdir(self.output_dir):
                files = [f for f in os.listdir(self.output_dir)
                         if os.path.isfile(os.path.join(self.output_dir, f))]
                if files:
                    _logger.info("Output: %s", files)
                    if elog:
                        elog.ok(f"Output files detected after {elapsed:.1f}s: {files}")
                    self._kill_jar()
                    return

            if os.path.isfile(os.path.join(self.jar_dir, 'tds.err')):
                _logger.info("Error report detected.")
                if elog:
                    elog.warn(f"Error report (tds.err) detected after {elapsed:.1f}s")
                self._kill_jar()
                return

            if not self._jar_alive():
                _logger.warning("JAR died before output.")
                if elog:
                    elog.error(f"JAR process died unexpectedly after {elapsed:.1f}s")
                raise RuntimeError("FVU JAR process exited unexpectedly.")

            time.sleep(1)

    def _kill_jar(self):
        if not self.jar_pid:
            return
        try:
            os.kill(self.jar_pid, 15)
        except ProcessLookupError:
            pass
        try:
            subprocess.run(['pkill', '-f', self.jar_file],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=5)
        except Exception:
            pass

    def _jar_alive(self):
        if self.jar_pid is None:
            return False
        try:
            os.kill(self.jar_pid, 0)
            return True
        except ProcessLookupError:
            return False

    def _cleanup(self):
        elog = self._log()
        if self.jar_pid:
            self._kill_jar()
            self.jar_pid = None
        if self.proc and self.proc.stdout:
            try:
                out, err = self.proc.communicate(timeout=5)
                if out and out.strip():
                    out_text = out.decode(errors='ignore')[:200]
                    _logger.info("JAR stdout: %s", out_text)
                    if elog:
                        elog.detail('JAR stdout (tail)', out_text)
                if err and err.strip():
                    err_text = err.decode(errors='ignore')[:200]
                    _logger.info("JAR stderr: %s", err_text)
                    if elog:
                        elog.detail('JAR stderr (tail)', err_text)
            except Exception:
                pass
        try:
            subprocess.run(['pkill', '-f', self.jar_file],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        if self.xvfb_pid:
            try:
                os.kill(self.xvfb_pid, 9)
                msg = f"Xvfb (PID {self.xvfb_pid}) stopped"
                _logger.info(msg)
            except ProcessLookupError:
                pass
            self.xvfb_pid = None

    def _collect_outputs(self):
        results = []
        elog = self._log()

        # 1. Output directory files (success case)
        if os.path.isdir(self.output_dir):
            for fname in os.listdir(self.output_dir):
                fpath = os.path.join(self.output_dir, fname)
                if os.path.isfile(fpath):
                    results.append(self._read_file(fpath))

        # 2. Error files from JAR directory
        for fname in ('tds.err', 'tdserr.html'):
            fpath = os.path.join(self.jar_dir, fname)
            if os.path.isfile(fpath):
                results.append(self._read_file(fpath))
                try:
                    shutil.move(fpath, os.path.join(self.tmp_dir, fname + '.bak'))
                except Exception:
                    pass

        # 3. Other .err/.html/.fvu files in tmp root
        INPUT_NAMES = {'tds.txt', 'challan.csi', 'consolidate.csi', 'consolidate.txt'}
        for fname in os.listdir(self.tmp_dir):
            fpath = os.path.join(self.tmp_dir, fname)
            if os.path.isfile(fpath) and fname.endswith(('.err', '.html', '.fvu')):
                if fname not in INPUT_NAMES:
                    results.append(self._read_file(fpath))

        _logger.info("Collected %d output files", len(results))
        if elog:
            elog.info(f"Collected {len(results)} output file(s) from temp directories")
            for r in results:
                elog.detail(f'  📄 {r["name"]}', f'{len(r["b64"]):,} bytes')

        return results

    @staticmethod
    def _read_file(path):
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        return {'name': os.path.basename(path), 'b64': data}
