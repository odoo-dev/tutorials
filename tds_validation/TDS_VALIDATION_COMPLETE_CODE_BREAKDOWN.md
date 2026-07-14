# TDS Validation Module — Complete Code Breakdown (v19.0.3)

## Table of Contents

1. [Module Overview](#1-module-overview)
2. [Module Structure](#2-module-structure)
3. [manifestpy --manifestpy](#3-manifestpy)
4. [initpy --initpy](#4-initpy)
5. [models/tds_validationpy](#5-modelstds_validationpy)
6. [services/fvu_runnerpy](#6-servicesfvu_runnerpy)
7. [services/version_checkerpy](#7-servicesversion_checkerpy)
8. [services/checksum_generatorpy](#8-serviceschecksum_generatorpy)
9. [services/validation_servicepy](#9-servicesvalidation_servicepy)
10. [services/log_servicepy](#10-serviceslog_servicepy)
11. [controllers/tds_controllerpy](#11-controllerstds_controllerpy)
12. [views/tds_validation_viewsxml](#12-viewstds_validation_viewsxml)
13. [security/ir/modelaccesscsv](#13-securityirmodelaccesscsv)
14. [data/irconfigparameterxml](#14-datairconfigparameterxml)
15. [client/tds_clientpy](#15-clienttds_clientpy)
16. [Execution Flow Summary](#16-execution-flow-summary)

---

## 1. Module Overview

This Odoo 19 module provides a complete **TDS/TCS FVU (File Validation Utility)** integration. It allows users to upload TDS tax files via the Odoo UI or a REST API, runs them through the government's Java-based FVU validation tool (headlessly), captures output files, and returns a detailed step-by-step execution log.

### Architecture: Client / Server split

```
┌─────────────────────────────────┐     HTTP/JSON      ┌─────────────────────────────────┐
│  CLIENT                          │     POST           │  SERVER (Odoo 19)               │
│  client/tds_client.py            │  ──────────────►   │  POST /api/tds/generate         │
│                                 │                    │                                 │
│  Standalone Python script       │     Response       │  tds_validation module          │
│  No Odoo dependencies           │  ◄──────────────   │  - Model (tds.validation)       │
│  Runs on any machine            │                    │  - Services (FVU, version, etc) │
│  Only needs: Python3 + requests  │                    │  - Controller (REST API)        │
└─────────────────────────────────┘                    └─────────────────────────────────┘
```

---

## 2. Module Structure

```
tds_validation/
├── __init__.py                  # Python package init (imports controllers, models, services)
├── __manifest__.py              # Odoo module manifest
├── TDS_VALIDATION_CODE_BREAKDOWN.md    # Original breakdown doc
├── TDS_VALIDATION_COMPLETE_CODE_BREAKDOWN.md  # This file
│
├── models/
│   ├── __init__.py              # Models package init
│   └── tds_validation.py        # Core Odoo model (tds.validation)
│
├── services/
│   ├── __init__.py              # Services package init
│   ├── fvu_runner.py            # FVU JAR runner (Xvfb + file polling)
│   ├── version_checker.py       # FVU version check against TIN server
│   ├── checksum_generator.py    # SHA-256 checksum generation/validation
│   ├── validation_service.py    # Pre-validation of file format & metadata
│   └── log_service.py           # Execution log capture & persistence
│
├── controllers/
│   ├── __init__.py              # Controllers package init
│   └── tds_controller.py        # REST API endpoint (/api/tds/generate)
│
├── views/
│   └── tds_validation_views.xml # Odoo UI views (form, list, menu, sequence)
│
├── security/
│   └── ir.model.access.csv      # Access rights for tds.validation model
│
├── data/
│   └── ir_config_parameter.xml  # Default system parameter (JAR directory)
│
├── client/
│   ├── __init__.py              # Client package init
│   └── tds_client.py            # Standalone CLI client (Python 3)
│
└── __pycache__/                 # Python bytecode cache
```

---

## 3. `__manifest__.py`

```python
{
    'name': 'TDS Validation',
    'version': '19.0.3.0.0',
    'summary': 'TDS FVU Validation — Production Grade — API + Checksum',
    'category': 'Tutorials',
    'author': 'Odoo',
    'depends': ['base', 'mail', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/tds_validation_views.xml',
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
```

**Line-by-line:**

- **`name`**: Human-readable module name shown in Odoo Apps
- **`version`**: `19.0.3.0.0` — Odoo 19.0, major 3, minor 0
- **`summary`**: Short description
- **`category`**: Appears under Tutorials in Apps list
- **`author`**: Module author
- **`depends`**: `base` (always), `mail` (chatter/threading features), `web` (web assets)
- **`data`**: Files loaded on install/upgrade — security, views, config parameters
- **`installable`**: Can be installed
- **`license`**: LGPL-3

---

## 4. `__init__.py`

### Module root — `tds_validation/__init__.py`

```python
from . import controllers
from . import models
from . import services
```

**Line-by-line:**

- Imports all three subpackages, triggering their respective `__init__.py` files
- **Order matters**: controllers depend on models, models depend on services

### `models/__init__.py`

```python
from . import tds_validation
```

### `services/__init__.py`

```python
from . import fvu_runner
from . import version_checker
from . import checksum_generator
from . import validation_service
from . import log_service
```

### `controllers/__init__.py`

```python
from . import tds_controller
```

### `client/__init__.py`

Empty file (marks `client/` as a Python package).

---

## 5. `models/tds_validation.py`

```python
import logging
import os

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from ..services.fvu_runner import FVURunner
from ..services.version_checker import FVUVersionChecker
from ..services.log_service import ExecutionLogger
```

**Lines 1-11 — Imports:**

- `logging`: Python's standard logging for debug/error messages
- `os`: Operating system utilities (file path operations)
- `api, models, fields`: Odoo framework for model definition, field types, and API decorators
- `UserError`: User-friendly error dialog in UI
- `ValidationError`: Field validation error
- `FVURunner`: Service that runs the Java FVU JAR headlessly
- `FVUVersionChecker`: Service that checks FVU version against TIN server
- `ExecutionLogger`: Service that captures step-by-step execution logs

```python
_logger = logging.getLogger(__name__)
```

**Line 13:**

- Creates a logger named `odoo.addons.tds_validation.models.tds_validation`

```python
VALID_TDS_EXTENSIONS = {'.txt', '.fvu'}
VALID_CSI_EXTENSION = '.csi'
```

**Lines 15-16:**

- Constants defining valid file extensions
- TDS/TCS files can be `.txt` or `.fvu`
- CSI (Challan) files must be `.csi`

---

```python
class TdsValidation(models.Model):
    _name = 'tds.validation'
    _description = 'TDS FVU Validation'
    _inherit = ['mail.thread']
    _order = 'create_date desc'
```

**Lines 18-22 — Class definition:**

- `_name = 'tds.validation'`: Database table name is `tds_validation`
- `_inherit = ['mail.thread']`: Adds chatter (message history, followers)
- `_order = 'create_date desc'`: Newest records first

---

### Fields

```python
name = fields.Char(
    string='Reference', required=True,
    default=lambda self: self.env['ir.sequence'].next_by_code('tds.validation') or 'New'
)
```

**Lines 24-27 — Reference field:**

- Auto-generated sequence number (e.g., `TDS/2026/0001`)
- Uses `ir.sequence` with code `tds.validation`
- Falls back to `'New'` if sequence not defined

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('running', 'Running'),
    ('done', 'Done'),
    ('failed', 'Failed'),
], default='draft', tracking=True)
```

**Lines 28-35 — State machine:**

- `draft`: Initial state — user uploads files
- `running`: Validation in progress
- `done`: Validation completed successfully
- `failed`: Validation failed with error
- `tracking=True`: Changes recorded in chatter

```python
tds_file = fields.Binary(
    string='TDS/TCS Input File',
    required=True,
    attachment=True,
    help='Upload .txt or .fvu file'
)
tds_filename = fields.Char(string='Filename')

consolidate_file = fields.Binary(
    string='Challan/Consolidate File (.csi)',
    attachment=True,
    help='Upload .csi file for correction statements'
)
consolidate_filename = fields.Char(string='Consolidate Filename')
```

**Lines 37-48 — Input file fields:**

- `tds_file`: Binary field storing the uploaded TDS file (base64 in DB)
- `attachment=True`: Files stored in Odoo's filestore, not in the DB column
- `tds_filename`: Stores original filename (referenced by `filename` attribute in XML)
- `consolidate_file`: Optional CSI (Challan) file for correction statements

```python
output_attachment_ids = fields.Many2many(
    'ir.attachment',
    'tds_val_att_rel', 'val_id', 'att_id',
    string='Output Files', readonly=True
)
error_message = fields.Text(readonly=True)
```

**Lines 50-54 — Output fields:**

- `output_attachment_ids`: Many2many to `ir.attachment` — stores FVU output files
- `tds_val_att_rel`: Relation table name in DB
- `error_message`: Read-only text field for failure details

```python
is_api_request = fields.Boolean(
    string='API Request',
    default=False,
    help='Created via REST API'
)
request_id = fields.Char(
    string='External Request ID',
    help='External reference from the calling system'
)
request_date = fields.Char(
    string='Request Date',
    help='Date from the external request (YYYY-MM-DD)'
)
notes = fields.Text(string='Notes')
checksum = fields.Char(
    string='Checksum',
    help='SHA-256 checksum of input files for integrity verification'
)
checksum_valid = fields.Boolean(
    string='Checksum Valid',
    default=False,
    help='Whether the provided checksum matched the computed value'
)
```

**Lines 56-81 — API / Integration fields:**

- `is_api_request`: Marks records created via REST API (affects UI visibility)
- `request_id`: External reference ID from calling system (e.g., "REQ-001")
- `request_date`: Date from external request (YYYY-MM-DD)
- `notes`: Free-text notes
- `checksum`: SHA-256 hex string provided by client
- `checksum_valid`: Boolean indicating whether checksum matched

```python
execution_log = fields.Text(
    string='Execution Log',
    readonly=True,
    help='Full step-by-step log of the validation execution'
)
```

**Lines 83-87 — Execution log:**

- Stores the complete timestamped log of the validation execution
- Populated by `ExecutionLogger` during `action_run_validation()`
- Returned to API clients and displayed in the Odoo form view

```python
fvu_version_local = fields.Char(string='Local FVU Version', readonly=True)
fvu_version_server = fields.Char(string='Server FVU Version', readonly=True)
fvu_version_status = fields.Selection([
    ('unknown', 'Unknown'),
    ('current', 'Up-to-date'),
    ('warn', 'Minor outdated'),
    ('old', 'Old'),
    ('unverified', 'Unverified'),
], string='FVU Version Status', default='unknown', readonly=True)
```

**Lines 89-99 — FVU version tracking:**

- Stores results from the version check against TIN server
- `fvu_version_local`: Version extracted from JAR filename (e.g., "9.4")
- `fvu_version_server`: Latest version from TIN server
- `fvu_version_status`: `current` / `warn` / `old` / `unverified` / `unknown`

---

### Config

```python
@api.model
def _get_jar_dir(self):
    """Read JAR directory from system parameters (single source of truth)."""
    return self.env['ir.config_parameter'].sudo().get_param(
        'tds_validation.jar_dir',
        '/home/odoo/Downloads/TDS_STANDALONE_FVU_9.4'
    )
```

**Lines 101-106 — Config method:**

- Reads JAR directory from `ir.config_parameter` (System Parameters)
- Defaults to `/home/odoo/Downloads/TDS_STANDALONE_FVU_9.4`
- Single source of truth — admin can change via Settings → System Parameters
- `sudo()` ensures even non-admin users can read it (it's data, not security)

---

### File Validation

```python
@api.onchange('tds_filename')
def _onchange_tds_filename(self):
    if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
        return {
            'warning': {
                'title': 'Invalid Extension',
                'message': 'TDS file must end with .txt or .fvu',
            }
        }

@api.onchange('consolidate_filename')
def _onchange_consolidate_filename(self):
    if self.consolidate_filename and not self._is_valid_csi_name(self.consolidate_filename):
        return {
            'warning': {
                'title': 'Invalid Extension',
                'message': 'Consolidate file must end with .csi',
            }
        }

@staticmethod
def _is_valid_tds_name(name):
    _, ext = os.path.splitext(name.lower())
    return ext in VALID_TDS_EXTENSIONS

@staticmethod
def _is_valid_csi_name(name):
    return name.lower().endswith(VALID_CSI_EXTENSION)
```

**Lines 108-131 — File extension validation:**

- `@api.onchange`: Triggered when user changes the filename field in UI
- Returns a warning dialog (non-blocking — user can still proceed)
- `_is_valid_tds_name()`: Checks `.txt` or `.fvu` extension (case-insensitive)
- `_is_valid_csi_name()`: Checks `.csi` extension

---

### Execution Log helpers

```python
def _reset_execution_log(self, log=None):
    """Clear execution log and optionally set initial message."""
    val = {'execution_log': False}
    if log:
        val['execution_log'] = log
    self.write(val)

def _append_execution_log(self, message):
    """Append a single line to execution_log."""
    current = self.execution_log or ''
    if current:
        current = current + '\n' + message
    else:
        current = message
    self.write({'execution_log': current})
```

**Lines 133-147 — Log helpers:**

- `_reset_execution_log()`: Clears the log field (used by action_reset)
- `_append_execution_log()`: Appends a single line (preserves existing content)
- These are kept for backward compatibility; the primary logging is via `ExecutionLogger`

---

### `action_run_validation()`

```python
def action_run_validation(self):
    self.ensure_one()

    # ── Init logger ──
    elog = ExecutionLogger(
        self,
        initial_step=f"=== TDS Validation START — {self.name} ===",
    )
    elog.detail('Validation ID', self.id)
    elog.detail('Request ID', self.request_id or 'N/A')
    elog.persist(self)
```

**Lines 149-157 — Initialization:**

- `self.ensure_one()`: Safety check — only one record at a time
- Creates `ExecutionLogger` instance, passing the record and initial message
- Logs validation ID and request ID
- `elog.persist()`: Immediately saves log to DB (so it's visible even if crash happens later)

```python
    if self.state == 'running':
        elog.error('Already in Running state — cannot start again.')
        elog.persist(self)
        raise UserError('Already running.')
```

**Lines 159-163 — State check:**

- Prevents double-triggering

```python
    # ── Validate required files ──
    if not self.tds_file:
        elog.error('TDS/TCS input file is missing.')
        elog.persist(self)
        raise UserError('Upload TDS/TCS Input File.')
    if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
        elog.error(f"Invalid TDS file extension: {self.tds_filename}")
        elog.persist(self)
        raise ValidationError('TDS file must end with .txt or .fvu')
    if self.consolidate_filename and not self._is_valid_csi_name(self.consolidate_filename):
        elog.error(f"Invalid CSI file extension: {self.consolidate_filename}")
        elog.persist(self)
        raise ValidationError('Consolidate file must end with .csi')

    elog.ok('Input file validation passed')
    elog.detail('TDS file', self.tds_filename or 'uploaded')
    if self.consolidate_filename:
        elog.detail('Consolidate file', self.consolidate_filename)
```

**Lines 165-180 — File validation:**

- Checks TDS file is uploaded
- Validates file extensions
- Logs success/failure at each sub-step
- `elog.persist()` before every `raise` to ensure log is saved before error propagates

```python
    # ── Checksum validation (if provided) ──
    if self.checksum:
        elog.section('Checksum Verification')
        elog.detail('Provided checksum', self.checksum)
        if self.checksum_valid:
            elog.ok('Checksum matched — data integrity verified')
        else:
            elog.warn('Checksum provided but not yet validated against computed value')
```

**Lines 182-188 — Checksum logging:**

- If checksum was provided (via API), log whether it validated or not
- `checksum_valid` is set by the controller before `action_run_validation` is called

```python
    # ── 1. Version check ──
    try:
        self._check_fvu_version(elog)
    except (UserError, ValidationError):
        elog.persist(self)
        raise
    except Exception:
        elog.error('Version check failed unexpectedly')
        elog.persist(self)
        raise
```

**Lines 190-198 — Version check:**

- Calls `_check_fvu_version()` which hits the TIN server
- If the version check raises an error (e.g., major mismatch), the validation stops
- All exceptions are logged before re-raising

```python
    # ── 2. State → Running ──
    elog.section('Launching FVU Validation')
    elog.info('Setting state to Running...')
    self.write({'state': 'running', 'error_message': False})
    self.env.cr.commit()
    elog.persist(self)
    elog.ok('State set to Running')
```

**Lines 200-206 — Set running state:**

- Sets state to 'running' and commits the DB transaction immediately
- This is critical — without the commit, the UI would hang until JAR finishes

```python
    # ── 3. Run JAR ──
    jar_dir = self._get_jar_dir()
    elog.detail('JAR directory', jar_dir)

    runner = FVURunner(self.id, jar_dir, elog)
    try:
        outputs = runner.run(
            tds_b64=self.tds_file,
            tds_filename=self.tds_filename,
            consolidate_b64=self.consolidate_file or None,
            consolidate_filename=self.consolidate_filename or None,
        )

        elog.section('Output Collection')
        elog.ok(f'FVU produced {len(outputs)} output file(s)')

        att_ids = []
        for f in outputs:
            elog.detail(f"  📄 {f['name']}", f"{len(f['b64']):,} bytes (base64)")
            att = self.env['ir.attachment'].create({
                'name': f['name'],
                'datas': f['b64'],
                'res_model': self._name,
                'res_id': self.id,
                'description': 'TDS FVU Output',
            })
            att_ids.append(att.id)

        elog.ok(f'Created {len(att_ids)} attachment(s) in Odoo filestore')

        self.write({
            'state': 'done',
            'output_attachment_ids': [(6, 0, att_ids)],
        })
        elog.section('COMPLETE')
        elog.ok(f'Validation completed successfully — {len(att_ids)} file(s) attached.')
        elog.persist(self)
        self.message_post(body=f"✅ Validation complete. {len(att_ids)} file(s) attached.")
```

**Lines 208-240 — JAR execution and output handling:**

- Creates `FVURunner` instance with record ID, JAR dir, and execution logger
- `runner.run()`: Executes the FVU JAR (or demo mode) and returns output files
- Each output file (base64-encoded) is saved as an `ir.attachment`
- `(6, 0, att_ids)`: "Replace all" command — sets output attachments
- Posts success message in chatter
- Finally, `elog.persist(self)` saves the complete log to DB

```python
    except Exception as e:
        elog.error(f'Validation failed: {e}')
        elog.persist(self)
        _logger.exception("TDS Validation failed [%s]", self.name)
        self.write({'state': 'failed', 'error_message': str(e)})
        self.message_post(body=f"❌ Failed: {e}")
        raise UserError(str(e)) from e
    finally:
        runner.cleanup()
        # Ensure the log is persisted even if something above failed
        try:
            if not self.execution_log:
                elog.persist(self)
        except Exception:
            pass
```

**Lines 242-253 — Error handling and cleanup:**

- `except`: Logs error, sets state to 'failed', saves error message, posts chatter message
- `finally`: Always runs `runner.cleanup()` (kills JAR, Xvfb, deletes temp dir)
- Ensures execution log is persisted even on failure path

---

### `_check_fvu_version()`

```python
def _check_fvu_version(self, elog=None):
    """Version check matching test.sh logic.

    Returns: result dict from checker.
    Raises UserError if major mismatch or server unreachable.
    """
    if elog is None:
        elog = ExecutionLogger(self)
    elog.section('FVU Version Check')

    jar_dir = self._get_jar_dir()
    elog.detail('JAR directory', jar_dir)

    checker = FVUVersionChecker(jar_dir)
    result = checker.check()

    elog.detail('Local version', result.get('local_version', 'N/A'))
    elog.detail('Server version', result.get('server_version', 'N/A'))
    elog.detail('Status', result.get('status', 'unknown'))
```

**Lines 255-272 — Version check setup:**

- Creates version checker, calls `result = checker.check()`
- Logs local version, server version, and status

```python
    status_map = {
        'error': 'unverified',
        'old': 'old',
        'warn': 'warn',
        'current': 'current',
    }

    # Persist version info regardless of outcome
    self.write({
        'fvu_version_local': result['local_version'],
        'fvu_version_server': result.get('server_version', ''),
        'fvu_version_status': status_map.get(result['status'], 'unknown'),
    })
```

**Lines 278-285 — Persist version info:**

- Maps internal status strings to display-friendly selection values
- Saves version info to model fields regardless of success/failure

```python
    if result['status'] == 'error':
        elog.error(f"Version check error: {result['message']}")
        elog.persist(self)
        raise UserError(result['message'])

    if result['status'] == 'old':
        elog.error(f"MAJOR version mismatch: {result['message']}")
        elog.persist(self)
        raise UserError(result['message'])

    if result['status'] == 'warn':
        elog.warn(result['message'])
        elog.persist(self)
        _logger.warning(result['message'])
        self.message_post(body=f"⚠ {result['message']}")
        return result

    elog.ok(result['message'])
    elog.persist(self)
    self.message_post(body=f"✅ {result['message']}")
    return result
```

**Lines 287-310 — Version check outcomes:**

- `error`: Server unreachable or JAR not found → blocks validation
- `old`: Major version mismatch (e.g., 9.4 vs 10.0) → blocks validation
- `warn`: Minor version outdated (e.g., 9.4 vs 9.5) → allows continuation with warning
- `current`: Versions match → green light with success message
- All outcomes are logged and persisted before returning

---

### `action_reset()`

```python
def action_reset(self):
    self.write({
        'state': 'draft',
        'error_message': False,
        'execution_log': False,
        'fvu_version_local': False,
        'fvu_version_server': False,
        'fvu_version_status': 'unknown',
    })
```

**Lines 312-320 — Reset action:**

- Resets state back to Draft
- Clears error message, execution log, and version info
- Allows user to retry with different files

---

## 6. `services/fvu_runner.py`

This is the most complex service — it runs the FVU Java JAR in a headless environment using Xvfb (virtual display server) and polls for output files.

### Imports and Constants

```python
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
```

**Lines 1-22:**

- `base64`: For encoding/decoding binary file data
- `subprocess`: For launching Xvfb and Java
- `tempfile`: For creating temporary directories
- `os`: File paths, process management (kill), env vars
- `shutil`: Recursive directory deletion
- `re`: Regex for extracting version from JAR filename
- `time`: Sleep intervals and elapsed time tracking
- `OUTPUT_TIMEOUT`: Maximum wait time for JAR to produce output (3 minutes)

```python
DEMO_MODE = os.environ.get('TDS_DEMO_MODE', '0') == '1'
DEMO_DELAY = 5  # seconds to simulate processing time
```

**Lines 24-30 — Demo mode:**

- When `TDS_DEMO_MODE=1` env var is set, skips the real JAR entirely
- Creates fake output files after a 5-second simulated delay
- Useful for testing the full pipeline without the government FVU utility

---

### Helper Functions

```python
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
```

**Lines 32-46 — JAR auto-detection:**

- Scans the JAR directory for files matching `TDS_STANDALONE_FVU_*.jar`
- Uses regex to extract version number (e.g., `9.4` from `TDS_STANDALONE_FVU_9.4.jar`)
- Sorts descending so highest version is found first
- Raises clear error if no JAR found

```python
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
```

**Lines 48-64 — Orphan cleanup:**

- Cleans up temp directories left by crashed runs
- Only removes directories older than 24 hours (configurable)
- Runs on every `FVURunner` initialization

---

### `FVURunner` Class

```python
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
```

**Lines 66-89 — Constructor:**

- Stores record ID, JAR directory, and execution logger
- Initializes tracking variables for temp dir, Xvfb PID, JAR PID, etc.
- Runs `_clean_orphan_temps()` to clean up from previous crashed runs
- **Demo mode**: If `TDS_DEMO_MODE=1`, skips JAR detection entirely
- **Production mode**: Auto-detects JAR file and version from the directory

```python
    def _log(self):
        """Access the ExecutionLogger (maybe None)."""
        return self.elog
```

**Lines 91-94 — Log helper:**

- Convenience method to access the `ExecutionLogger`
- Returns `None` if no logger was provided (graceful fallback)

---

### `run()` method

```python
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
```

**Lines 96-114 — Run method:**

- If demo mode is active, delegates to `_run_demo()` immediately
- Otherwise continues with real JAR execution

```python
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
```

**Lines 116-140 — File preparation:**

- Creates temp directory with `_create_temp_dir()`
- Writes TDS file and optional CSI file to temp directory (decoded from base64)
- Sets up error output path (JAR writes errors here)

```python
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
```

**Lines 142-154 — Execution:**

- Starts Xvfb (virtual display)
- Launches the JAR
- Waits for output files to appear (polling)
- Collects and returns output files
- `finally` block always runs `_cleanup()` to kill processes

---

### `_run_demo()` method

```python
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

    fname_stem = os.path.splitext(tds_filename or 'TDS')[0]
    if elog:
        elog.info(f'Simulating FVU processing ({DEMO_DELAY}s delay)...')

    for i in range(DEMO_DELAY):
        time.sleep(1)
        if elog:
            elog.detail(f'  Processing...', f'{i+1}/{DEMO_DELAY}s')

    if elog:
        elog.ok('FVU processing complete')

    # Creates 2 demo output files:
    # 1. test_tds_FVU_4.fvu — main FVU output with fake deductee data
    # 2. test_tds_Summary.rpt — fake summary report with PANs and amounts

    if elog:
        elog.ok(f'Created {len(output_files)} demo output file(s)')

    results = [self._read_file(fp) for fp in output_files]
    return results
```

**Lines 156-220 — Demo mode:**

- Simulates the full FVU processing pipeline without real JAR
- Logs every step identically to production mode
- Creates realistic-looking fake `.fvu` and `.rpt` output files
- Saves files to temp directory, reads them back as base64

---

### Internal Methods

**`_create_temp_dir()` — Lines 234-240:**

```python
def _create_temp_dir(self):
    self.tmp_dir = tempfile.mkdtemp(prefix=f'tds_{self.record_id}_')
    self.output_dir = os.path.join(self.tmp_dir, 'output')
    os.makedirs(self.output_dir)
```

- Creates `/tmp/tds_{record_id}_{random}/` and `output/` subdirectory

**`_write_file()` — Lines 242-245:**

```python
@staticmethod
def _write_file(path, b64_data):
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64_data))
    return path
```

- Decodes base64 to raw bytes, writes to file

**`_find_free_display()` — Lines 247-250:**

```python
@staticmethod
def _find_free_display():
    n = 200
    while os.path.exists(f'/tmp/.X{n}-lock'):
        n += 1
    return n
```

- Finds an available X display number starting at 200
- Avoids conflict with real displays (usually `:0`)

**`_start_xvfb()` — Lines 252-262:**

```python
def _start_xvfb(self):
    n = self._find_free_display()
    self.display = f':{n}'
    proc = subprocess.Popen(
        ['Xvfb', self.display, '-screen', '0', '1280x800x24'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    self.xvfb_pid = proc.pid
    time.sleep(1)
```

- Starts Xvfb (virtual framebuffer) — a display server that doesn't need a physical monitor
- FVU JAR is a Java Swing GUI app that needs a display to render
- 1280×800 resolution, 24-bit color
- 1-second sleep for Xvfb to initialize

**`_build_env()` — Lines 264-280:**

```python
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
    return env
```

- **Critical fix**: Builds a clean environment to avoid Snap/VS Code contamination
- Only copies `HOME`, `USER`, `LANG` from parent process
- `GIO_MODULE_DIR` → empty dir: prevents GLib from loading stale Snap plugins (caused "failed to map segment" crash)
- `GTK_MODULES = ''`: Prevents GTK from loading extra modules
- `NO_AT_BRIDGE = '1'`: Disables accessibility bridge
- `GDK_BACKEND = 'x11'`: Forces GTK to use X11 (compatible with Xvfb)

**`_launch_jar()` — Lines 282-312:**

```python
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

    self.proc = subprocess.Popen(
        cmd, cwd=self.jar_dir, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    self.jar_pid = self.proc.pid
```

- Builds the Java command: `java -Xmx512m ... -jar TDS_STANDALONE_FVU_9.4.jar [arguments]`
- JVM args limit memory to prevent OOM:
  - `-Xmx512m`: Max heap 512MB
  - `-XX:MaxMetaspaceSize=256m`: Limit metadata
  - `-XX:CompressedClassSpaceSize=256m`: Limit class space
- JAR arguments:
  1. TDS input file path
  2. Error output file path
  3. Output directory (with trailing slash — required by JAR)
  4. `0`: Placeholder parameter
  5. JAR version (e.g., `9.4`)
  6. `1`: Mode flag (CLI mode)
  7. Consolidate file path (or empty string)
- Linux: The JAR is launched with a clean environment in the background

**`_wait_for_output()` — Lines 314-350:**

```python
def _wait_for_output(self, timeout=OUTPUT_TIMEOUT):
    _logger.info("Polling for output (timeout=%ds)...", timeout)
    start = time.time()

    while True:
        elapsed = time.time() - start
        if elapsed > timeout:
            self._kill_jar()
            raise TimeoutError(...)

        if os.path.isdir(self.output_dir):
            files = [f for f in os.listdir(self.output_dir)
                     if os.path.isfile(os.path.join(self.output_dir, f))]
            if files:
                self._kill_jar()
                return

        if os.path.isfile(os.path.join(self.jar_dir, 'tds.err')):
            self._kill_jar()
            return

        if not self._jar_alive():
            raise RuntimeError("FVU JAR process exited unexpectedly.")

        time.sleep(1)
```

- Polls every 1 second for output files (up to 180 seconds)
- **Success detection**: Any file appears in output directory → JAR completed
- **Error detection**: `tds.err` appears in JAR directory → error report generated
- **Crash detection**: JAR process no longer alive → unexpected exit
- Immediately kills JAR once output is detected (prevents popup dialogs from blocking)

**`_kill_jar()` — Lines 352-363:**

- Sends SIGTERM (signal 15) to the Java process
- Falls back to `pkill -f` for any zombie child processes

**`_jar_alive()` — Lines 365-371:**

- Uses `os.kill(pid, 0)` — signal 0 doesn't kill, just checks if process exists

**`_cleanup()` — Lines 373-395:**

- Kills JAR if still running
- Reads any remaining stdout/stderr from the process (for debugging)
- Kills Xvfb with SIGKILL (signal 9)
- All operations wrapped in try/except to avoid partial cleanup

**`_collect_outputs()` — Lines 397-427:**

```python
def _collect_outputs(self):
    results = []

    # 1. Output directory files (success case)
    if os.path.isdir(self.output_dir):
        for fname in os.listdir(self.output_dir):
            ...

    # 2. Error files from JAR_DIR
    for fname in ('tds.err', 'tdserr.html'):
        ...

    # 3. Other .err/.html/.fvu files in tmp root
    INPUT_NAMES = {'tds.txt', 'challan.csi', 'consolidate.csi', 'consolidate.txt'}
    for fname in os.listdir(self.tmp_dir):
        ...

    return results
```

- Collects from 3 sources:
  1. Output directory (.fvu files from success)
  2. JAR directory (tds.err, tdserr.html from errors)
  3. Temp root (any other .err/.html/.fvu files)
- Excludes input files from the results

---

## 7. `services/version_checker.py`

```python
import logging
import os
import re
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

**Lines 1-16 — Imports:**

- `requests`: HTTP client for POST to TIN server
- `urllib3`: Disables SSL warnings (TIN server uses self-signed cert)

```python
DEMO_MODE = os.environ.get('TDS_DEMO_MODE', '0') == '1'

VERSION_URL = 'https://onlineservices.tin.egov.proteantech.in/TIN/checkfvuversion.do'
TIMEOUT = 15
```

**Lines 18-21:**

- `DEMO_MODE`: When set, skips the real server check
- `VERSION_URL`: The TIN government server endpoint for version checking
- `TIMEOUT`: 15-second HTTP timeout

---

### `get_local_version()` function

```python
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
```

**Lines 23-41 — Version detection:**

- Same logic as `_detect_jar_info()` in fvu_runner.py
- Extracts version from JAR filename using regex
- Returns `(version, None)` on success, `(None, error_message)` on failure

---

### `FVUVersionChecker` class

```python
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
```

**Lines 43-58 — Check method with demo mode:**

- In demo mode, returns a fake "current" status immediately
- In production, proceeds with real server check

```python
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
```

**Lines 60-99 — Full check logic:**

- Detects local version from JAR filename
- Fetches latest version from TIN server via HTTP POST
- Server response format: `"9.5^2.191^2.1321^1.1"` — first field is the version
- Server unreachable or empty response → error (blocks validation)
- Compares versions and returns result

```python
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
```

**Lines 101-119 — Server communication:**

- POSTs to TIN server with `fvu_version=1` parameter
- `verify=False`: TIN server uses self-signed SSL certificate
- Returns raw response text (e.g., `"9.5^2.191^2.1321^1.1"`)

```python
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
```

**Lines 121-149 — Version comparison logic:**

- Parses both versions into `(major, minor)` tuples
- **Major mismatch** (e.g., 9 vs 10): Blocks validation with error
- **Minor outdated** (e.g., 9.4 vs 9.5): Warns but allows continuation
- **Current**: Returns success
- **Unparseable**: Falls back to string equality comparison

---

## 8. `services/checksum_generator.py`

```python
import base64
import hashlib
import logging

_logger = logging.getLogger(__name__)

class ChecksumGenerator:
    """Generates and validates SHA-256 checksums for TDS input files."""
```

**Lines 1-9:**

- SHA-256 checksum generation and validation
- Used by the API controller for data integrity verification

```python
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
            _logger.warning(...)
            sha.update(tds_b64.encode('utf-8'))

        # Optionally include CSI file in hash
        if csi_b64:
            try:
                csi_raw = base64.b64decode(csi_b64)
                sha.update(csi_raw)
            except Exception as e:
                _logger.warning(...)
                sha.update(csi_b64.encode('utf-8'))

        checksum = sha.hexdigest()
        return checksum
```

**Lines 11-44 — Generate method:**

- Creates SHA-256 hash of base64-decoded file contents
- If CSI file is provided, includes it in the hash as well
- Fallback: if base64 decode fails, hashes the raw base64 string
- Returns hex-encoded digest

```python
    @staticmethod
    def validate(tds_b64, csi_b64, expected_checksum):
        """
        Validate that the generated checksum matches the expected value.
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
```

**Lines 46-60 — Validate method:**

- Generates checksum and compares with expected value
- Returns boolean
- Logs success or failure

---

## 9. `services/validation_service.py`

```python
import base64
import logging
import os

_logger = logging.getLogger(__name__)

class ValidationService:
    """Validates TDS input data integrity and format."""
```

**Lines 1-9:**

- Pre-validation service called by the API controller before running FVU JAR

```python
    @staticmethod
    def validate_file_format(filename, file_b64):
        """
        Validate file extension and basic content integrity.
        """
        errors = []

        if not filename:
            return {'valid': False, 'error': 'Filename is required.'}

        _, ext = os.path.splitext(filename.lower())
        valid_extensions = {'.txt', '.fvu', '.csi'}
        if ext not in valid_extensions:
            return {
                'valid': False,
                'error': f"Invalid extension '{ext}'. Allowed: .txt, .fvu, .csi"
            }

        if not file_b64:
            return {'valid': False, 'error': 'File content is empty.'}

        try:
            decoded = base64.b64decode(file_b64, validate=True)
            if len(decoded) == 0:
                return {'valid': False, 'error': 'Decoded file content is empty.'}
        except Exception as e:
            return {'valid': False, 'error': f"Invalid base64 encoding: {e}"}

        return {'valid': True, 'error': None}
```

**Lines 11-40 — File format validation:**

- Checks: filename exists, extension valid (`.txt`, `.fvu`, `.csi`), base64 content decodes correctly

```python
    @staticmethod
    def validate_metadata(data):
        """
        Validate request metadata fields.
        """
        errors = []

        request_id = data.get('request_id', '')
        request_date = data.get('request_date', '')

        if request_id and not isinstance(request_id, str):
            errors.append("request_id must be a string.")

        if request_date:
            import re
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(request_date)):
                errors.append("request_date must be in YYYY-MM-DD format.")

        return {'valid': len(errors) == 0, 'errors': errors}
```

**Lines 42-58 — Metadata validation:**

- `request_id` must be a string if provided
- `request_date` must be YYYY-MM-DD format if provided

```python
    @staticmethod
    def pre_validate_all(tds_b64, tds_filename, csi_b64=None, csi_filename=None, metadata=None):
        """
        Run all pre-validations and return a summary.
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
```

**Lines 60-99 — Pre-validate all:**

- Runs all validations in a single call
- Returns consolidated result with `valid`, `errors`, `warnings`
- Metadata is optional

---

## 10. `services/log_service.py`

This service captures a detailed execution log for each validation run and stores it on the `tds.validation` record.

```python
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class ExecutionLogger:
    """Captures execution logs and stores them on a tds.validation record."""
```

**Lines 1-9:**

- Standard logging + datetime imports
- `ExecutionLogger` class

```python
    def __init__(self, record=None, initial_step=None):
        """
        Args:
            record: tds.validation record (optional, to persist logs).
            initial_step: optional initial message.
        """
        self.record = record
        self._lines = []
        if initial_step:
            self._add_line(initial_step)
```

**Lines 11-19 — Constructor:**

- Stores reference to Odoo record for persistence
- Initializes empty lines list
- Optionally adds initial message (e.g., "=== Validation START ===")

---

### Logging methods

```python
    def section(self, title):
        """Log a section heading with markers."""
        self._add_line(f"\n{'─' * 55}")
        self._add_line(f"  {title}")
        self._add_line(f"{'─' * 55}")
```

**Lines 22-27 — Section heading:**

- Creates a visual separator like:
  ```
  ───────────────────────────────────────────────────────
    FVU Version Check
  ───────────────────────────────────────────────────────
  ```

```python
    def info(self, msg):
        """Log an informational message."""
        self._add_line(f"  {msg}")
        _logger.info("[TDS %s] %s", self._rec_id(), msg)

    def ok(self, msg):
        """Log a success message."""
        self._add_line(f"  ✅ {msg}")
        _logger.info("[TDS %s] OK: %s", self._rec_id(), msg)

    def warn(self, msg):
        """Log a warning message."""
        self._add_line(f"  ⚠ {msg}")
        _logger.warning("[TDS %s] WARN: %s", self._rec_id(), msg)

    def error(self, msg):
        """Log an error message."""
        self._add_line(f"  ❌ ERROR: {msg}")
        _logger.error("[TDS %s] ERROR: %s", self._rec_id(), msg)

    def detail(self, label, value):
        """Log a key-value detail pair."""
        self._add_line(f"  · {label}: {value}")
        _logger.info("[TDS %s] %s = %s", self._rec_id(), label, value)

    def raw(self, text):
        """Log a raw line (no prefix)."""
        self._add_line(text)
```

**Lines 29-62 — Logging methods:**

- Each method does **dual logging**: captures line in-memory AND writes to Odoo logger
- Emoji prefixes: ✅ for success, ⚠ for warning, ❌ for error, · for detail
- Odoo logger prefix includes record ID for traceability

```python
    def persist(self, record=None):
        """Write the accumulated log to the model's execution_log field."""
        rec = record or self.record
        if rec is not None:
            try:
                rec.write({'execution_log': self.get_log()})
                self.record = rec
            except Exception as e:
                _logger.warning("Could not persist execution log: %s", e)

    def get_log(self):
        """Return the full log as a single string."""
        return '\n'.join(self._lines)
```

**Lines 64-74 — Persistence:**

- `persist()`: Writes the current accumulated log to the DB record's `execution_log` field
- Called frequently during validation (after each major step) to ensure log is saved even on crash
- `get_log()`: Returns all lines joined by newline

```python
    def _add_line(self, line):
        """Add a timestamped line."""
        ts = datetime.now().strftime('%H:%M:%S')
        self._lines.append(f"[{ts}] {line}")

    def _rec_id(self):
        if self.record and self.record.id:
            return f"rec#{self.record.id}"
        return '?'
```

**Lines 76-83 — Internal:**

- Each log line is prefixed with a timestamp like `[05:56:11]`
- `_rec_id()`: Returns human-readable record ID for Odoo logger

---

## 11. `controllers/tds_controller.py`

```python
import json
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class TDSGeneratorController(http.Controller):

    @http.route('/api/tds/generate', type='jsonrpc', methods=['POST'], auth='user', csrf=False)
    def generate_tds(self, **kwargs):
```

**Lines 1-22 — Controller setup:**

- `type='jsonrpc'`: Uses Odoo's JSON-RPC protocol (avoiding deprecation warning from `type='json'`)
- `auth='user'`: Requires authenticated user session
- `csrf=False`: Disables CSRF for API calls (handled by session auth)

---

### `generate_tds()` method

**Step 1 — Parse input (lines 25-42):**

```python
        params = request.params if hasattr(request, 'params') else kwargs
        data = params.get('params') or params
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                data = params
```

- Handles multiple JSON-RPC request formats
- Extracts the parameters from the JSON-RPC envelope

**Step 2 — Validate required fields (lines 48-62):**

```python
        errors = []
        if not tds_b64:
            errors.append("tds_file_b64 is required.")
        if not tds_filename:
            errors.append("tds_filename is required.")
        if tds_filename and not (tds_filename.lower().endswith('.txt') or ...):
            errors.append("tds_filename must end with .txt or .fvu")
        if csi_filename and not csi_filename.lower().endswith('.csi'):
            errors.append("csi_filename must end with .csi")
        if errors:
            return self._response('error', '; '.join(errors))
```

- Validates required fields presence and extension

**Step 3 — Checksum validation (lines 64-80):**

```python
        checksum_valid = None
        computed_checksum = ''
        if checksum_input:
            checksum_valid = self._validate_checksum(
                tds_b64, csi_b64, checksum_input
            )
```

- If checksum was provided, validates it against computed value
- On mismatch, logs warning and computes alternative checksum for debugging

**Step 4 — Create tds.validation record (lines 82-96):**

```python
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
```

- Creates a new `tds.validation` record in Draft state
- Sets `is_api_request = True` so the UI shows API-related fields

**Step 5 — Run validation (lines 98-103):**

```python
        try:
            validation.action_run_validation()
        except Exception as run_e:
            _logger.exception("FVU run failed for validation %s", validation.id)
            pass
```

- Calls the model's `action_run_validation()` method
- Catches exceptions but **does not fail the API request** — the record's state is already set to 'failed' by the model
- The error_message and execution_log are preserved

**Step 6 — Collect output (lines 105-110):**

- Reads output attachments and encodes them as base64

**Step 7 — Collect execution log (line 112):**

```python
        execution_log = validation.execution_log or ''
```

**Build response (lines 114-130):**

```python
        response_data = {
            'validation_id': validation.id,
            'reference': validation.name,
            'state': validation.state,
            'output_files': output_files,
            'error_message': validation.error_message or '',
            'execution_log': execution_log,
        }
```

- Returns all data including the full execution log

```python
        return self._response('ok', 'TDS validation processed.', response_data)
```

---

### Helper methods

```python
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
```

**Lines 136-147 — Checksum validation:**

- Uses `ChecksumGenerator` service
- Gracefully handles missing service module

```python
    @staticmethod
    def _response(status, message, data=None):
        """Build standardized JSON response."""
        result = {'status': status, 'message': message}
        if data:
            result['data'] = data
        return result
```

**Lines 149-154 — Response builder:**

- Standardized response format: `{ status, message, data? }`

---

## 12. `views/tds_validation_views.xml`

### Sequence

```xml
<record id="seq_tds_validation" model="ir.sequence">
    <field name="name">TDS Validation</field>
    <field name="code">tds.validation</field>
    <field name="prefix">TDS/%(year)s/</field>
    <field name="padding">4</field>
</
```
