import base64
import logging
import os
import shutil
import signal
import subprocess
import tempfile
import time

_logger = logging.getLogger(__name__)

OUTPUT_TIMEOUT = 10


class FVURunner:
    """Run FVU JAR under Xvfb, collect outputs, clean up."""

    def __init__(self, record_id, jar_dir):
        self.record_id = record_id
        self.jar_path = os.path.join(jar_dir, 'TDS_STANDALONE_FVU_9.4.jar')
        if not os.path.isfile(self.jar_path):
            raise FileNotFoundError(f"JAR not found: {self.jar_path}")

        self.tmp_dir = None
        self.output_dir = None
        self.xvfb_proc = None
        self.jar_proc = None

    def run(self, tds_b64, tds_filename, csi_b64=None, csi_filename=None):
        """Run JAR with given files, return list of {name, b64} outputs."""
        try:
            self._setup()

            tds_path = self._write_file(tds_filename or 'tds.txt', tds_b64)
            csi_path = ''
            if csi_b64:
                csi_path = self._write_file(csi_filename or 'challan.csi', csi_b64)

            self._start_xvfb()
            self._launch_jar(tds_path, csi_path)
            outputs = self._wait_and_collect()
            return outputs

        finally:
            self._cleanup()

    def _setup(self):
        self.tmp_dir = tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')
        self.output_dir = os.path.join(self.tmp_dir, 'output')
        os.makedirs(self.output_dir, exist_ok=True)

    def _write_file(self, filename, b64_data):
        path = os.path.join(self.tmp_dir, filename)
        with open(path, 'wb') as f:
            f.write(base64.b64decode(b64_data))
        return path

    def _start_xvfb(self):
        n = 200
        while os.path.exists(f'/tmp/.X{n}-lock'):
            n += 1
        display = f':{n}'
        self.xvfb_proc = subprocess.Popen(['Xvfb', display, '-screen', '0', '1280x800x24'],
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, )
        time.sleep(1)

        env = os.environ.copy()
        env['DISPLAY'] = display
        env['GTK_MODULES'] = ''
        env['NO_AT_BRIDGE'] = '1'
        env['GDK_BACKEND'] = 'x11'
        # Empty GIO dir prevents GLib from loading system modules (thread-safe)
        gio_dir = os.path.join(self.tmp_dir, 'gio-empty')
        os.makedirs(gio_dir, exist_ok=True)
        env['GIO_MODULE_DIR'] = gio_dir
        self._env = env

    def _launch_jar(self, tds_path, csi_path):
        err_path = os.path.join(self.output_dir, 'fvuerror.err')
        cmd = ['java', '-Xmx512m', '-XX:CompressedClassSpaceSize=256m', '-XX:MaxMetaspaceSize=256m', '-jar',
               self.jar_path, tds_path, err_path, self.output_dir + '/', '0', '9.4', '1', csi_path or '', ]
        self.jar_proc = subprocess.Popen(cmd, cwd=os.path.dirname(self.jar_path), env=self._env,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE, )

    def _wait_and_collect(self):
        """Wait for output files, kill JAR, return collected outputs."""
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > OUTPUT_TIMEOUT:
                self._kill_jar()
                raise TimeoutError(
                    f"JAR did not produce output within {OUTPUT_TIMEOUT}s"
                )

            # Check for output files
            if os.path.isdir(self.output_dir):
                files = [f for f in os.listdir(self.output_dir)
                         if os.path.isfile(os.path.join(self.output_dir, f))]
                if files:
                    self._kill_jar()
                    return self._collect()

            # Check for error file in jar directory
            jar_dir = os.path.dirname(self.jar_path)
            if os.path.isfile(os.path.join(jar_dir, 'tds.err')):
                self._kill_jar()
                return self._collect()

            # Check if JAR exited
            if self.jar_proc.poll() is not None:
                stdout, stderr = self.jar_proc.communicate(timeout=5)
                raise RuntimeError(
                    f"JAR exited unexpectedly. stderr: "
                    f"{stderr.decode(errors='ignore')[:200]}"
                )

            time.sleep(1)

    def _collect(self):
        """Collect all output files -> [{name, b64}]."""
        results = []

        # From output directory
        if os.path.isdir(self.output_dir):
            for fname in sorted(os.listdir(self.output_dir)):
                fpath = os.path.join(self.output_dir, fname)
                if os.path.isfile(fpath):
                    results.append(self._read_b64(fpath))

        # Error files from jar dir
        jar_dir = os.path.dirname(self.jar_path)
        for err_name in ('tds.err', 'tdserr.html'):
            err_path = os.path.join(jar_dir, err_name)
            if os.path.isfile(err_path):
                results.append(self._read_b64(err_path))
                try:
                    shutil.move(err_path, os.path.join(self.tmp_dir, err_name))
                except Exception:
                    pass

        return results

    @staticmethod
    def _read_b64(path):
        with open(path, 'rb') as f:
            return {'name': os.path.basename(path), 'b64': base64.b64encode(f.read()).decode()}

    def _kill_jar(self):
        """Kill JAR and Xvfb processes."""
        if self.jar_proc and self.jar_proc.poll() is None:
            try:
                subprocess.run(['xdotool', 'search', '--name', 'FVU', 'windowkill'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=3)
            except Exception:
                pass
            self.jar_proc.send_signal(signal.SIGTERM)
            try:
                self.jar_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.jar_proc.kill()
                self.jar_proc.wait(timeout=5)

        # pkill fallback
        try:
            subprocess.run(['pkill', '-f', 'TDS_STANDALONE_FVU'], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           timeout=5)
        except Exception:
            pass

        if self.xvfb_proc and self.xvfb_proc.poll() is None:
            self.xvfb_proc.kill()
            self.xvfb_proc.wait(timeout=5)

    def cleanup(self):
        self._cleanup()

    def _cleanup(self):
        """Remove temp directory."""
        self._kill_jar()
        if self.tmp_dir and os.path.isdir(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)
