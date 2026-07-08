# TDS Validation Module — Complete Code Breakdown

## Table of Contents
1. [Module Structure](#1-module-structure)
2. [`__manifest__.py`](#2-__manifest__py)
3. [`__init__.py`](#3-__init__py)
4. [`models/tds_validation.py`](#4-modelstd_validationpy)
5. [`services/fvu_runner.py`](#5-servicesfvu_runnerpy)
6. [`views/tds_validation_views.xml`](#6-viewstds_validation_viewsxml)
7. [`security/ir.model.access.csv`](#7-securityirmodelaccesscsv)
8. [Reference Bash Script (`run_fvu_cli.sh`)](#8-reference-bash-script-run_fvu_clish)
9. [Execution Flow Summary](#9-execution-flow-summary)

---

## 1. Module Structure

```
tds_validation/
├── __init__.py                  # Python package init
├── __manifest__.py              # Odoo module manifest
├── models/
│   ├── __init__.py              # Models package init
│   └── tds_validation.py        # Core Odoo model (tds.validation)
├── services/
│   ├── __init__.py              # Services package init
│   └── fvu_runner.py            # FVU JAR runner service
├── views/
│   └── tds_validation_views.xml # Odoo UI views (form, list, menu)
└── security/
    └── ir.model.access.csv      # Access rights for tds.validation model
```

---

## 2. `__manifest__.py`

```python
{
    'name': 'TDS Validation',
    'version': '19.0.1.0.0',
    'summary': 'Run TDS FVU validation from Odoo via CLI',
    'category': 'Tutorials',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_validation_views.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
```

**Line-by-line:**
- **`name`**: Human-readable module name shown in Odoo Apps
- **`version`**: Odoo 19.0, major version 1, minor 0
- **`summary`**: Short description of what the module does
- **`category`**: Where the module appears in the Apps list
- **`depends`**: `base` (always required) and `mail` (for chatter/threading features)
- **`data`**: Files loaded on install/upgrade — security rights first, then views
- **`installable`**: Whether the module can be installed
- **`license`**: LGPL-3 open-source license

---

## 3. `__init__.py`

```python
from . import models
from . import services
```

**Line-by-line:**
- **`from . import models`**: Imports the `models/` subpackage, which triggers `models/__init__.py`
- **`from . import services`**: Imports the `services/` subpackage, which triggers `services/__init__.py`

Both files inside those subdirectories (`__init__.py` files) handle importing specific modules.

---

## 4. `models/tds_validation.py`

```python
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from ..services.fvu_runner import FVURunner
```

**Line-by-line:**
- **`import logging`**: Python's standard logging library for debug/error messages
- **`from odoo import models, fields, api`**: Odoo framework imports — `models` for model classes, `fields` for field types, `api` for Odoo API decorators
- **`from odoo.exceptions import UserError`**: Exception class for showing user-friendly error dialogs
- **`from ..services.fvu_runner import FVURunner`**: Imports the service class that actually runs the JAR file

---

```python
_logger = logging.getLogger(__name__)
```

**Line-by-line:**
- **`logging.getLogger(__name__)`**: Creates a logger named `odoo.addons.tds_validation.models.tds_validation` for log messages

---

```python
class TdsValidation(models.Model):
    _name        = 'tds.validation'
    _description = 'TDS FVU Validation'
    _inherit     = ['mail.thread']
    _order       = 'create_date desc'
```

**Line-by-line:**
- **`class TdsValidation(models.Model)`**: Defines a new Odoo model class
- **`_name = 'tds.validation'`**: Database table name is `tds_validation`; referenced in XML as `model_tds_validation`
- **`_description = 'TDS FVU Validation'`**: Human-readable description for Odoo's internal use
- **`_inherit = ['mail.thread']`**: Inherits `mail.thread` so the record has a "chatter" (message history with followers)
- **`_order = 'create_date desc'`**: Default ordering: newest records first

---

```python
name = fields.Char(
    string='Reference', required=True,
    default=lambda self: self.env['ir.sequence'].next_by_code('tds.validation') or 'New'
)
```

**Line-by-line:**
- **`name`**: A Char field used as the record's display name
- **`string='Reference'`**: Label shown in the UI (not "Name")
- **`required=True`**: Must have a value
- **`default=lambda self: ...`**: Auto-generates a sequence number using `ir.sequence` with code `tds.validation`; falls back to `'New'` if no sequence defined

---

```python
state = fields.Selection([
    ('draft',   'Draft'),
    ('running', 'Running'),
    ('done',    'Done'),
    ('failed',  'Failed'),
], default='draft', tracking=True)
```

**Line-by-line:**
- **`state`**: A selection (dropdown) field for workflow status
- **`('draft', 'Draft')`**: Initial state — user uploads files
- **`('running', 'Running')`**: Validation is in progress
- **`('done', 'Done')`**: Validation completed successfully
- **`('failed', 'Failed')`**: Validation failed with an error
- **`default='draft'`**: New records start in Draft state
- **`tracking=True`**: Changes to this field are recorded in the chatter

---

```python
# ── Input files ───────────────────────────────────────────────
tds_file          = fields.Binary(string='TDS/TCS Input File (.txt)', required=True)
tds_filename      = fields.Char()
challan_file      = fields.Binary(string='Challan File (.csi)', required=True)
challan_filename  = fields.Char()
consolidate_file  = fields.Binary(string='Consolidate File (optional)')
consolidate_filename = fields.Char()
```

**Line-by-line:**
- **`tds_file`**: Binary field that stores the uploaded TDS file as base64 in the database
- **`required=True`**: Must be provided before saving
- **`tds_filename`**: Stores the original filename (used by the `binary` widget's `filename` attribute)
- **`challan_file`**: Binary field for the challan (.csi) file
- **`challan_filename`**: Stores the challan file's original name
- **`consolidate_file`**: Optional binary field for a consolidate file
- **`consolidate_filename`**: Stores the consolidate file's original name

---

```python
# ── Output ────────────────────────────────────────────────────
output_attachment_ids = fields.Many2many(
    'ir.attachment',
    'tds_val_att_rel', 'val_id', 'att_id',
    string='Output Files', readonly=True
)
error_message = fields.Text(readonly=True)
```

**Line-by-line:**
- **`output_attachment_ids`**: Many2many relationship linking to `ir.attachment` records
- **`'ir.attachment'`**: Odoo's built-in file storage model (stores files in database or filestore)
- **`'tds_val_att_rel'`**: Name of the relation table in the database
- **`'val_id'`**: Column in the relation table pointing to `tds.validation` ID
- **`'att_id'`**: Column pointing to `ir.attachment` ID
- **`readonly=True`**: Users cannot manually edit — only the code sets it
- **`error_message`**: Read-only text field that stores error details on failure

---

```python
def action_run_validation(self):
    self.ensure_one()
```

**Line-by-line:**
- **`def action_run_validation(self)`**: Method called when user clicks "Run Validation" button
- **`self.ensure_one()`**: Raises an error if `self` contains more than one record (safety check)

---

```python
    if self.state == 'running':
        raise UserError("Already running.")
    if not self.tds_file:
        raise UserError("Upload TDS/TCS Input File.")
    if not self.challan_file:
        raise UserError("Upload Challan File.")
```

**Line-by-line:**
- **State check**: Prevents double-triggering if already running
- **File checks**: Validates required files are uploaded before proceeding

---

```python
    self.write({'state': 'running', 'error_message': False})
    self.env.cr.commit()  # show Running in UI immediately
```

**Line-by-line:**
- **`self.write(...)`**: Updates the record's state to 'running' and clears any previous error
- **`self.env.cr.commit()`**: Commits the current database transaction so the UI immediately shows "Running" (otherwise it would hang until the JAR finishes)

---

```python
    runner = FVURunner(self.id)
    try:
        outputs = runner.run(
            tds_b64=self.tds_file,
            tds_filename=self.tds_filename,
            challan_b64=self.challan_file,
            challan_filename=self.challan_filename,
            consolidate_b64=self.consolidate_file or None,
            consolidate_filename=self.consolidate_filename or None,
        )
```

**Line-by-line:**
- **`runner = FVURunner(self.id)`**: Creates an instance of the FVU Runner service, passing the record ID for logging
- **`runner.run(...)`**: Executes the JAR with the uploaded file data (as base64 strings)
- **`outputs`**: Returns a list of dicts, each with `name` and `b64` (base64-encoded file content)

---

```python
        # Create attachments
        att_ids = []
        for f in outputs:
            att = self.env['ir.attachment'].create({
                'name':        f['name'],
                'datas':       f['b64'],
                'res_model':   self._name,
                'res_id':      self.id,
                'description': 'TDS FVU Output',
            })
            att_ids.append(att.id)

        self.write({
            'state': 'done',
            'output_attachment_ids': [(6, 0, att_ids)],
        })
        self.message_post(body=f"✅ Validation complete. {len(att_ids)} file(s) attached.")
```

**Line-by-line:**
- **`att_ids = []`**: Empty list to collect attachment IDs
- **`for f in outputs:`**: Iterates over each output file
- **`self.env['ir.attachment'].create({...})`**: Creates an attachment record in Odoo's file storage
  - `name`: The output filename (e.g., `TDS_FVU_123.fvu` or `tdserr.html`)
  - `datas`: The base64-encoded file content
  - `res_model` / `res_id`: Links the attachment to the current `tds.validation` record
- **`self.write({'state': 'done', 'output_attachment_ids': [(6, 0, att_ids)]})`**: Sets state to Done and links all attachments using the "replace all" command `(6, 0, [ids])`
- **`self.message_post(...)`**: Posts a success message in the chatter

---

```python
    except Exception as e:
        _logger.exception("TDS Validation failed [%s]", self.name)
        self.write({'state': 'failed', 'error_message': str(e)})
        self.message_post(body=f"❌ Failed: {e}")
        raise UserError(str(e)) from e
```

**Line-by-line:**
- **`except Exception as e`**: Catches any exception during JAR execution
- **`_logger.exception(...)`**: Logs the full traceback to the server log
- **`self.write(...)`**: Sets state to Failed and saves the error message
- **`self.message_post(...)`**: Posts a failure message in the chatter
- **`raise UserError(str(e)) from e`**: Re-raises a user-friendly error dialog in the UI

---

```python
    finally:
        runner.cleanup()
```

**Line-by-line:**
- **`finally:`**: Runs whether validation succeeds or fails
- **`runner.cleanup()`**: Deletes the temporary directory created by `FVURunner`

---

```python
def action_reset(self):
    self.write({'state': 'draft', 'error_message': False})
```

**Line-by-line:**
- **`action_reset`**: Resets a Failed record back to Draft so the user can try again
- **`self.write(...)`**: Sets state back to Draft and clears the error message

---

## 5. `services/fvu_runner.py`

This is the most complex file — it handles the interaction with the TDS FVU Java JAR.

```python
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
```

**Line-by-line:**
- **Docstring**: Explains the purpose — runs the JAR with Xvfb (virtual display) and uses file polling (not xdotool) to detect completion. The `GIO_MODULE_DIR` fix prevents a specific GLib crash when running inside VS Code's Snap environment.
- **`import base64`**: For encoding/decoding binary file data
- **`import logging`**: For logging messages
- **`import os`**: For file paths, process management (kill), and env vars
- **`import shutil`**: For deleting temp directories (`rmtree`)
- **`import subprocess`**: For launching external processes (Xvfb, Java)
- **`import tempfile`**: For creating temporary directories
- **`import time`**: For sleep intervals

---

```python
_logger = logging.getLogger(__name__)
```

**Line-by-line:**
- Creates a logger named `odoo.addons.tds_validation.services.fvu_runner`

---

```python
# ── Config ────────────────────────────────────────────────────────────────────
JAR_DIR = '/home/odoo/Downloads/TDS_STANDALONE_FVU_1.0'
JAR_FILE = 'TDS_STANDALONE_FVU_1.0.jar'
JAR_VERSION = '1.0'
```

**Line-by-line:**
- **`JAR_DIR`**: Absolute path to the directory containing the FVU JAR and its dependencies
- **`JAR_FILE`**: The filename of the FVU executable JAR
- **`JAR_VERSION`**: Passed as an argument to the JAR to specify which version to use

---

```python
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
```

**Line-by-line:**
- **`class FVURunner`**: A service class — one instance per validation run
- **`__init__(self, record_id)`**: Constructor; stores the Odoo record ID for temp dir naming
- **`self.tmp_dir`**: Temporary directory path (set later)
- **`self.output_dir`**: Subdirectory inside `tmp_dir` where JAR writes results
- **`self.xvfb_pid`**: PID of the Xvfb process (for cleanup)
- **`self.display`**: The virtual display number (e.g., `:204`)
- **`self.jar_pid`**: PID of the Java process
- **`self.proc`**: The `subprocess.Popen` object for the Java process

---

```python
    # ── Public ────────────────────────────────────────────────────────────────

    def run(self, tds_b64, tds_filename, challan_b64, challan_filename,
            consolidate_b64=None, consolidate_filename=None):
```

**Line-by-line:**
- **`def run(...)`**: The main public method called by `tds_validation.py`
- **Parameters**: Base64-encoded file content and original filenames; `consolidate_*` is optional

---

```python
        try:
            self._create_temp_dir()
            tds_path = self._write_file(tds_filename or 'tds.txt', tds_b64)
            challan_path = self._write_file(challan_filename or 'challan.csi', challan_b64)
            consolidate_path = ''
            if consolidate_b64:
                consolidate_path = self._write_file(
                    consolidate_filename or 'consolidate.txt', consolidate_b64)

            err_path = os.path.join(self.tmp_dir, 'err.err')
```

**Line-by-line:**
- **`self._create_temp_dir()`**: Creates a temp directory like `/tmp/tds_42_abc123/` and an `output/` subdir
- **`self._write_file(...)`**: Decodes base64 → writes to a file in the temp dir → returns the file path
- **`consolidate_path`**: Defaults to empty string if no consolidate file provided
- **`err_path`**: The error output file path (JAR writes error info here)

---

```python
            self._start_xvfb()
            self._launch_jar(tds_path, err_path, self.output_dir, consolidate_path)
            self._wait_for_output()
```

**Line-by-line:**
- **`self._start_xvfb()`**: Starts a virtual X server (needed because the FVU JAR is a GUI app)
- **`self._launch_jar(...)`**: Launches the Java process in background
- **`self._wait_for_output()`**: Polls in a loop until the JAR creates output files or times out

---

```python
            return self._collect_outputs()
```

**Line-by-line:**
- **`self._collect_outputs()`**: Gathers all output files from the output dir and error dir, reads them as base64, returns a list of dicts

---

```python
        except Exception as e:
            _logger.error("Validation failed: %s", e)
            raise

        finally:
            self._cleanup()
```

**Line-by-line:**
- **`except`**: Logs and re-raises any exception
- **`finally`**: Guarantees cleanup (kill JAR, kill Xvfb) even if an error occurred

---

```python
    def cleanup(self):
        self._cleanup()
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)
            _logger.info("Cleaned up: %s", self.tmp_dir)
```

**Line-by-line:**
- **`cleanup()`**: Called from `tds_validation.py`'s `finally` block (separate from `_cleanup` because `_cleanup` kills processes, then `cleanup` also deletes the temp directory)
- **`shutil.rmtree(...)`**: Recursively deletes the entire temp directory
- **`ignore_errors=True`**: Don't crash if files are already deleted

---

```python
    # ── Internal ──────────────────────────────────────────────────────────────

    def _create_temp_dir(self):
        self.tmp_dir = tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')
        self.output_dir = os.path.join(self.tmp_dir, 'output')
        os.makedirs(self.output_dir)
        _logger.info("Temp dir: %s", self.tmp_dir)
```

**Line-by-line:**
- **`tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')`**: Creates a secure temp directory. Example: `/tmp/tds_42_a1b2c3d/`
- **`self.output_dir = os.path.join(self.tmp_dir, 'output')`**: Full path to the `output/` subdirectory
- **`os.makedirs(self.output_dir)`**: Creates the `output/` directory

---

```python
    def _write_file(self, filename, b64_data):
        path = os.path.join(self.tmp_dir, filename)
        with open(path, 'wb') as f:
            f.write(base64.b64decode(b64_data))
        _logger.info("Wrote: %s", path)
        return path
```

**Line-by-line:**
- **`base64.b64decode(b64_data)`**: Decodes the base64 string back to raw binary bytes
- **`open(path, 'wb')`**: Opens a file in write-binary mode
- **`f.write(...)`**: Writes the decoded bytes to the file
- **Returns**: The full file path

---

```python
    def _find_free_display(self):
        num = 200
        while os.path.exists(f'/tmp/.X{num}-lock'):
            num += 1
        return num
```

**Line-by-line:**
- **`_find_free_display()`**: Finds an available X display number
- **Starts at 200**: Avoids conflict with real displays (usually `:0`)
- **`/tmp/.X{num}-lock`**: X server creates a lock file for each used display number
- **Returns**: The first free display number

---

```python
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
```

**Line-by-line:**
- **`Xvfb`**: "X Virtual Framebuffer" — a virtual display server that doesn't need a physical monitor
- **`-screen '0' '1280x800x24'`**: Creates screen 0 with 1280×800 resolution, 24-bit color depth
- **`subprocess.Popen(...)`**: Launches Xvfb in the background (non-blocking)
- **`stdout=subprocess.DEVNULL`**: Discards Xvfb's output
- **`time.sleep(1)`**: Gives Xvfb time to initialize before we set `DISPLAY` and launch the JAR

---

```python
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
```

**Line-by-line:**
- **`env = {}`**: Starts with a fresh, empty environment dictionary
- **Only copies `HOME`, `USER`, `LANG`**: Avoids inheriting Snap-contaminated environment variables like `GTK_PATH`, `GIO_MODULE_DIR`, `LOCPATH` from VS Code
- **`DISPLAY`**: Points to our Xvfb virtual display
- **`PATH`**: Sets a clean, minimal PATH (no Snap bin dirs)
- **`GIO_MODULE_DIR`**: **Critical fix** — points GLib's module system to an empty directory so it doesn't load stale cached plugins from the Snap runtime (which caused `failed to map segment` errors)
- **`GTK_MODULES = ''`**: Prevents GTK from loading extra modules
- **`NO_AT_BRIDGE = '1'`**: Disables the accessibility bridge (another GLib consumer that can crash)
- **`GDK_BACKEND = 'x11'`**: Forces GTK to use X11 backend (compatible with Xvfb)

---

```python
    def _launch_jar(self, tds_path, err_path, output_dir, consolidate_path=''):
        jar_path = os.path.join(JAR_DIR, JAR_FILE)
        if not os.path.isfile(jar_path):
            raise FileNotFoundError(f"JAR not found: {jar_path}")
```

**Line-by-line:**
- **`jar_path`**: Full path to the FVU JAR file
- **`os.path.isfile(jar_path)`**: Checks if the JAR actually exists at the expected location
- **`raise FileNotFoundError(...)`**: Stops early with a clear error if the JAR is missing

---

```python
        env = self._build_env()

        jvm_args = [
            '-Xmx512m',
            '-XX:CompressedClassSpaceSize=256m',
            '-XX:MaxMetaspaceSize=256m',
        ]
```

**Line-by-line:**
- **`env = self._build_env()`**: Gets the clean environment
- **`-Xmx512m`**: Limits JVM heap to 512MB (prevents out-of-memory)
- **`-XX:CompressedClassSpaceSize=256m`**: Limits compressed class space to 256MB (default is 1GB, which can fail on low-memory systems)
- **`-XX:MaxMetaspaceSize=256m`**: Limits metadata space to 256MB

---

```python
        cmd = (
            ['java'] + jvm_args + ['-jar', jar_path]
            + [tds_path, err_path, output_dir + '/', '0', JAR_VERSION, '1']
            + ([consolidate_path] if consolidate_path else [''])
        )
```

**Line-by-line:**
This constructs the command line as:
```
java -Xmx512m -XX:CompressedClassSpaceSize=256m -XX:MaxMetaspaceSize=256m
    -jar /path/to/TDS_STANDALONE_FVU_1.0.jar
    /tmp/tds_42_xxx/tds.txt        # TDS input file
    /tmp/tds_42_xxx/err.err        # Error output file
    /tmp/tds_42_xxx/output/        # Output directory (trailing slash)
    0                               # Unused parameter
    1.0                             # JAR version
    1                               # Some mode flag
    ""                              # Consolidate file (empty if not used)
```
- **`output_dir + '/'`**: The JAR expects a trailing slash on the output directory path
- **`'0'`**: Placeholder parameter (the original CLI expects this)
- **`JAR_VERSION`**: Currently `'1.0'`
- **`'1'`**: Mode flag (1 = CLI mode)
- **`consolidate_path`**: Optional path to consolidate file, or empty string

---

```python
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
```

**Line-by-line:**
- **`subprocess.Popen(...)`**: Launches the Java process in background (non-blocking)
- **`cwd=JAR_DIR`**: Sets the working directory to the JAR directory (JAR's relative dependencies — like the `.jar` libs — are resolved from here)
- **`env=env`**: Uses the clean environment (not inherited from Odoo)
- **`stdout=subprocess.PIPE, stderr=subprocess.PIPE`**: Captures stdout and stderr so we can read them later
- **`self.jar_pid`**: Stores the process ID for later cleanup

---

```python
    def _wait_for_output(self, timeout=180):
        """
        Poll for output files — mirrors the bash script's while-true loop.
        Detects completion when:
        - 'tds.err' AND 'tdserr.html' exist in JAR_DIR (error)
        - Any file appears in output_dir (success)
        """
        _logger.info("Polling for output files (timeout=%ds)...", timeout)
        start = time.time()
```

**Line-by-line:**
- **`timeout=180`**: Maximum time to wait (3 minutes)
- **File-polling approach**: Instead of using `xdotool` to dismiss a dialog, this watches for the output files the JAR would create. This is more reliable in headless/Snap environments.

---

```python
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                _logger.warning("Timeout (%ds) reached — no output files detected", timeout)
                return
```

**Line-by-line:**
- **Infinite loop** with time check
- **`time.time() - start`**: Calculates elapsed seconds
- **Returns silently** (no exception) if timeout is reached — the caller will see 0 output files collected

---

```python
            # Error files generated in JAR_DIR
            tds_err = os.path.join(JAR_DIR, 'tds.err')
            tds_err_html = os.path.join(JAR_DIR, 'tdserr.html')
            if os.path.isfile(tds_err) and os.path.isfile(tds_err_html):
                _logger.info("Validation completed (Error report generated).")
                return
```

**Line-by-line:**
- **`JAR_DIR` error files**: The FVU JAR writes `tds.err` and `tdserr.html` to its own directory when validation fails (matching the bash script's behavior)
- **Both must exist**: The JAR creates both files simultaneously when it produces an error report

---

```python
            # Success: any file in output_dir
            if os.path.isdir(self.output_dir):
                files = [f for f in os.listdir(self.output_dir)
                         if os.path.isfile(os.path.join(self.output_dir, f))]
                if files:
                    _logger.info("Validation completed (Output generated): %s", files)
                    return

            time.sleep(1)
```

**Line-by-line:**
- **`os.listdir(self.output_dir)`**: Lists all entries in the output directory
- **Filters out subdirectories** (only counts files)
- **Any file detected**: Means the JAR produced its `.fvu` output
- **`time.sleep(1)`**: Waits 1 second between polls (avoids busy-waiting)

---

```python
    def _cleanup(self):
        """Kill JAR first, then Xvfb — mirrors bash trap cleanup."""
        if self.jar_pid:
            try:
                os.kill(self.jar_pid, 15)
                _logger.info("JAR (PID %d) stopped", self.jar_pid)
            except ProcessLookupError:
                pass
            self.jar_pid = None
```

**Line-by-line:**
- **`os.kill(self.jar_pid, 15)`**: Sends SIGTERM (signal 15) to the Java process — asks it to shut down gracefully
- **`ProcessLookupError`**: Ignored if the process already exited on its own

---

```python
        if self.proc and self.proc.stdout:
            try:
                out, err = self.proc.communicate(timeout=5)
                if out and out.strip():
                    _logger.info("JAR remainder stdout: %s", out.decode(errors='ignore')[:300])
                if err and err.strip():
                    _logger.info("JAR remainder stderr: %s", err.decode(errors='ignore')[:300])
            except Exception:
                pass
```

**Line-by-line:**
- **`proc.communicate(timeout=5)`**: Reads any remaining buffered stdout/stderr from the process (with a 5-second timeout)
- **`out.decode(errors='ignore')`**: Decodes bytes to string, ignoring invalid characters
- **`[:300]`**: Truncates long messages to 300 characters
- Used for debugging: captures any last output from the JAR

---

```python
        try:
            subprocess.run(['pkill', '-f', JAR_FILE],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
```

**Line-by-line:**
- **`pkill -f TDS_STANDALONE_FVU_1.0.jar`**: Kills any remaining Java processes matching the JAR filename (safety net in case there are zombie child processes)

---

```python
        if self.xvfb_pid:
            try:
                os.kill(self.xvfb_pid, 9)
                _logger.info("Xvfb %s stopped", self.display)
            except ProcessLookupError:
                pass
            self.xvfb_pid = None
```

**Line-by-line:**
- **`os.kill(self.xvfb_pid, 9)`**: Sends SIGKILL (signal 9) to Xvfb — forceful kill because Xvfb doesn't always respond to SIGTERM

---

```python
    def _collect_outputs(self):
        """
        Collect output files from:
        - output_dir (success .fvu files)
        - tmp_dir root for .err/.html/.fvu
        - JAR_DIR error files (tds.err, tdserr.html) — per bash script logic
        """
        results = []
```

**Line-by-line:**
- Returns a list of dicts: `[{'name': 'filename', 'b64': 'base64string'}, ...]`

---

```python
        # 1. Output dir files (success case)
        if os.path.isdir(self.output_dir):
            for fname in os.listdir(self.output_dir):
                fpath = os.path.join(self.output_dir, fname)
                if os.path.isfile(fpath):
                    results.append(self._read_file(fpath))
```

**Line-by-line:**
- **First**: Collects any `.fvu` output files from the output directory (success case)

---

```python
        # 2. Error files from JAR_DIR (matching bash script)
        for fname in ('tds.err', 'tdserr.html'):
            fpath = os.path.join(JAR_DIR, fname)
            if os.path.isfile(fpath):
                results.append(self._read_file(fpath))
                try:
                    shutil.move(fpath, os.path.join(self.tmp_dir, fname + '.bak'))
                except Exception:
                    pass
```

**Line-by-line:**
- **Second**: Collects error report files from the JAR directory (error case)
- **`shutil.move(...)`**: Moves the error files to the temp directory with a `.bak` suffix to prevent them from being re-collected in a subsequent run

---

```python
        # 3. Other .err/.html/.fvu files in tmp_dir root
        for fname in os.listdir(self.tmp_dir):
            fpath = os.path.join(self.tmp_dir, fname)
            if os.path.isfile(fpath) and fname.endswith(('.err', '.html', '.fvu')):
                if fname not in ('tds.txt', 'challan.csi', 'consolidate.txt', 'err.err'):
                    results.append(self._read_file(fpath))
```

**Line-by-line:**
- **Third**: Collects any other error/HTML/FVU files that may have been written to the temp dir root (e.g., `tdserr.html` copied from `JAR_DIR`)
- **Excludes input files** (`tds.txt`, `challan.csi`, `consolidate.txt`, `err.err`) so we don't re-upload the user's own files

---

```python
        _logger.info("Collected %d output files", len(results))
        return results

    def _read_file(self, path):
        with open(path, 'rb') as f:
            data = base64.b64encode(f.read()).decode()
        return {'name': os.path.basename(path), 'b64': data}
```

**Line-by-line:**
- **`_read_file(path)`**: Reads a file from disk and encodes it as base64
- **`base64.b64encode(f.read()).decode()`**: Reads raw bytes → encodes to base64 bytes → decodes to string
- **`os.path.basename(path)`**: Extracts just the filename (e.g., `tdserr.html` not `/full/path/tdserr.html`)

---

## 6. `views/tds_validation_views.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
```

**Line-by-line:**
- Standard Odoo data file opening tags

---

```xml
    <record id="seq_tds_validation" model="ir.sequence">
        <field name="name">TDS Validation</field>
        <field name="code">tds.validation</field>
        <field name="prefix">TDS/%(year)s/</field>
        <field name="padding">4</field>
    </record>
```

**Line-by-line:**
- **Creates an `ir.sequence` record**: Auto-numbering sequence
- **`code`**: `tds.validation` — the same code used in the model's `default` for the `name` field
- **`prefix`**: Format `TDS/2026/` (prefix + current year + `/`)
- **`padding`**: Zero-pads the number to 4 digits → `TDS/2026/0001`

---

```xml
    <record id="view_tds_validation_form" model="ir.ui.view">
        <field name="name">tds.validation.form</field>
        <field name="model">tds.validation</field>
        <field name="arch" type="xml">
            <form string="TDS Validation">
```

**Line-by-line:**
- **Defines a Form view**: The main form layout
- **`model="tds.validation"`**: Attached to our custom model

---

```xml
                <header>
                    <button name="action_run_validation" type="object"
                            string="▶ Run Validation" class="btn-primary"
                            invisible="state not in ['draft']"/>
                    <button name="action_reset" type="object"
                            string="Reset to Draft"
                            invisible="state not in ['failed']"/>
                    <field name="state" widget="statusbar"
                           statusbar_visible="draft,running,done,failed"/>
                </header>
```

**Line-by-line:**
- **`header`**: Odoo's smart buttons area at the top
- **"Run Validation" button**: Calls `action_run_validation()`, visible only in Draft state
- **"Reset to Draft" button**: Calls `action_reset()`, visible only in Failed state
- **`state` field**: Shown as a `statusbar` widget showing all four states

---

```xml
                <sheet>
                    <div class="oe_title">
                        <h1><field name="name" readonly="1"/></h1>
                    </div>

                    <group string="Input Files">
                        <field name="tds_file" widget="binary"
                               filename="tds_filename"
                               string="TDS/TCS Input File (.txt)"
                               readonly="state != 'draft'"/>
                        <field name="tds_filename" invisible="1"/>

                        <field name="challan_file" widget="binary"
                               filename="challan_filename"
                               string="Challan File (.csi)"
                               readonly="state != 'draft'"/>
                        <field name="challan_filename" invisible="1"/>

                        <field name="consolidate_file" widget="binary"
                               filename="consolidate_filename"
                               string="Consolidate File (optional)"
                               readonly="state != 'draft'"/>
                        <field name="consolidate_filename" invisible="1"/>
                    </group>
```

**Line-by-line:**
- **`sheet`**: Main editable content area
- **`oe_title`**: Odoo standard title styling
- **`widget="binary"`**: Shows a file upload widget (drag-and-drop or browse)
- **`filename="tds_filename"`**: Tells the widget to store the original filename in the `tds_filename` field
- **`invisible="1"`**: The filename Char fields are hidden from the UI (only used programmatically)
- **`readonly="state != 'draft'"`**: File uploads are only editable in Draft state

---

```xml
                    <group string="Error Details"
                           invisible="state != 'failed'">
                        <field name="error_message" readonly="1" nolabel="1"/>
                    </group>
```

**Line-by-line:**
- **Visible only in Failed state**: Shows the error details
- **`nolabel="1"`**: Hides the field's label (error text is self-explanatory)

---

```xml
                    <notebook invisible="state != 'done'">
                        <page string="Output Files">
                            <field name="output_attachment_ids"
                                   widget="many2many_binary" readonly="1"/>
                        </page>
                    </notebook>
```

**Line-by-line:**
- **`notebook`**: Tabbed section, visible only in Done state
- **`widget="many2many_binary"`**: Shows downloadable file links for each attachment
- Users can click to download the `.fvu` files, error reports, etc.

---

```xml
                </sheet>
                <chatter/>
            </form>
        </field>
    </record>
```

**Line-by-line:**
- **`chatter/`**: Odoo's communication widget — shows messages, logs, and followers
- Inherited from `['mail.thread']` in the model

---

```xml
    <record id="view_tds_validation_list" model="ir.ui.view">
        <field name="name">tds.validation.list</field>
        <field name="model">tds.validation</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="tds_filename"/>
                <field name="state" widget="badge"
                       decoration-success="state == 'done'"
                       decoration-danger="state == 'failed'"
                       decoration-warning="state == 'running'"
                       decoration-muted="state == 'draft'"/>
                <field name="create_date"/>
            </list>
        </field>
    </record>
```

**Line-by-line:**
- **List (tree) view**: Shows a table of all TDS Validation records
- **Columns**: Reference name, input filename, state (colored badge), creation date
- **`widget="badge"`**: Shows state as colored pills
- **`decoration-*`**: Colors the row based on state (green=done, red=failed, yellow=running, muted=draft)

---

```xml
    <record id="action_tds_validation" model="ir.actions.act_window">
        <field name="name">TDS Validation</field>
        <field name="res_model">tds.validation</field>
        <field name="view_mode">list,form</field>
    </record>

    <menuitem id="menu_tds_root" name="TDS Validation" sequence="99"/>
    <menuitem id="menu_tds_list" name="Validations"
              parent="menu_tds_root" action="action_tds_validation" sequence="1"/>
</odoo>
```

**Line-by-line:**
- **`act_window`**: Defines a menu action that opens the model's list view (with form view accessible)
- **`menuitem`**: Creates a top-level menu "TDS Validation" with submenu "Validations"
- **`sequence="99"`**: Pushes the menu to the far right of the Odoo navbar

---

## 7. `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_tds_validation_user,tds.validation.user,model_tds_validation,base.group_user,1,1,1,1
```

**Line-by-line:**
- **CSV header**: `id, name, model_id, group_id, read, write, create, unlink`
- **`access_tds_validation_user`**: Unique ID for this access rule
- **`tds.validation.user`**: Human-readable name
- **`model_id:id`**: `model_tds_validation` — Odoo's auto-generated model reference (snake_case of model name)
- **`group_id:id`**: `base.group_user` — all internal users (Employees group)
- **`1,1,1,1`**: Full CRUD access (read, write, create, delete) for all internal users

---

## 8. Reference Bash Script (`run_fvu_cli.sh`)

```bash
#!/bin/bash
TDS_FILE="$1"
ERR_FILE="$2"  
OUTPUT_DIR="$3"
JAR_DIR="/home/odoo/Downloads/TDS_STANDALONE_FVU_1.0"
JAR_FILE="TDS_STANDALONE_FVU_1.0.jar"
```

**Line-by-line:**
- **`TDS_FILE="$1"`**: First command-line argument: path to TDS input file
- **`ERR_FILE="$2"`**: Second argument: path to error output file
- **`OUTPUT_DIR="$3"`**: Third argument: directory for output files
- **`JAR_DIR`**: Hardcoded path to the FVU JAR directory
- **`JAR_FILE`**: JAR filename

---

```bash
# Free display
DISPLAY_NUM=200
while [ -e "/tmp/.X${DISPLAY_NUM}-lock" ]; do DISPLAY_NUM=$((DISPLAY_NUM+1)); done
```

**Line-by-line:**
- Same logic as `_find_free_display()` in the Python code
- Starts at 200 and increments until it finds a free display number (no lock file)

---

```bash
# Start Xvfb
Xvfb ":$DISPLAY_NUM" -screen 0 1280x800x24 2>/dev/null &
XVFB_PID=$!
sleep 1

export DISPLAY=":$DISPLAY_NUM"
```

**Line-by-line:**
- **`Xvfb ... &`**: Starts Xvfb in background
- **`XVFB_PID=$!`**: Captures the background process's PID
- **`sleep 1`**: Wait for Xvfb to initialize
- **`export DISPLAY`**: Sets the display number for child processes

---

```bash
# Run JAR CLI mode
cd "$JAR_DIR"
java -jar "$JAR_FILE" "$TDS_FILE" "$ERR_FILE" "$OUTPUT_DIR" 0 1.0 1 "" &
JAR_PID=$!
```

**Line-by-line:**
- **`cd "$JAR_DIR"`**: Changes to the JAR directory before running
- **Same arguments** as the Python version: input file, error file, output dir, `0`, `1.0`, `1`, `""`
- **`&`**: Runs in background; `JAR_PID=$!` captures PID

---

```bash
# Wait for Message popup then dismiss
for i in $(seq 1 60); do
    DIALOG=$(xdotool search --name "Message" 2>/dev/null | tail -1)
    if [ -n "$DIALOG" ]; then
        echo "[OK] Dialog found — dismissing"
        xdotool windowfocus --sync "$DIALOG"
        xdotool key Return
        break
    fi
    sleep 1
done
```

**Line-by-line:**
- **`xdotool search --name "Message"`**: Searches for a visible window titled "Message" (the FVU JAR's popup dialog)
- **`xdotool windowfocus --sync "$DIALOG"`**: Brings the dialog window to focus
- **`xdotool key Return`**: Presses Enter to dismiss it
- **Poll every 1 second** for up to 60 seconds
- **Note**: The Python version replaced this with `_wait_for_output()` (file polling) because `xdotool` doesn't work reliably in the Snap environment (it needs access to the X server, and Xvfb + Snap has permission issues)

---

```bash
wait $JAR_PID

# Cleanup
kill $XVFB_PID 2>/dev/null

echo "=== Output files ==="
ls -lh "$OUTPUT_DIR"
```

**Line-by-line:**
- **`wait $JAR_PID`**: Blocks until the JAR process exits
- **`kill $XVFB_PID`**: Kills Xvfb after the JAR finishes
- **`ls -lh "$OUTPUT_DIR"`**: Lists the output files

---

## 9. Execution Flow Summary

### Step-by-step what happens when user clicks "Run Validation":

```
User clicks "▶ Run Validation"
        │
        ▼
[1] Model: action_run_validation()
    ├── Checks state (must be 'draft')
    ├── Checks required files uploaded
    ├── Sets state → 'running'
    ├── Commits DB (so UI shows "Running")
    │
    ▼
[2] Service: FVURunner(self.id)
    ├── Creates temp dir /tmp/tds_{id}_{random}/
    │   └── output/ subdirectory
    ├── Decodes base64 files → writes to temp dir
    │   ├── tds.txt, challan.csi, [consolidate.txt]
    │   └── err.err (empty, for JAR to fill)
    │
    ▼
[3] Start Xvfb (virtual display)
    ├── Finds free display # (starting at 200)
    └── Launches Xvfb in background
    │
    ▼
[4] Build clean environment
    ├── Only HOME, USER, LANG from parent
    ├── DISPLAY → our Xvfb
    ├── GIO_MODULE_DIR → empty dir (*** GLib crash fix ***)
    ├── GTK_MODULES='', NO_AT_BRIDGE=1
    └── GDK_BACKEND=x11
    │
    ▼
[5] Launch JAR (background)
    ├── java -Xmx512m -XX:CompressedClassSpaceSize=256m ...
    ├── Arguments: input files, output dir, version flags
    └── Runs in JAR_DIR (for relative classpath)
    │
    ▼
[6] Poll for output files (up to 180s)
    ├── Every 1 second, check:
    │   ├── tds.err + tdserr.html in JAR_DIR → Error
    │   └── Any file in output/ → Success
    └── Returns when detected (or timeout)
    │
    ▼
[7] Collect output files
    ├── Read output/*.fvu (success)
    ├── Read JAR_DIR/tds.err + tdserr.html (error)
    └── Encode all as base64, return list of dicts
    │
    ▼
[Back to Model]
[8] Create ir.attachment records
    ├── For each output: name + base64 data
    ├── Link to tds.validation record
    ├── Set state → 'done'
    └── Post success message in chatter
    │
    ▼
[9] Cleanup (finally block)
    ├── Kill JAR (SIGTERM)
    ├── pkill any leftover Java
    ├── Kill Xvfb (SIGKILL)
    ├── Delete temp directory
    └── Done!
```

### Error path (if anything fails):
```
[Any step fails]
        │
        ▼
   Catch Exception
   ├── Set state → 'failed'
   ├── Save error_message
   ├── Post failure message in chatter
   └── Show UserError dialog in UI
