"""
Execution Log Service
---------------------
Captures a detailed step-by-step execution log for each TDS validation run.
Stores the log on the `tds.validation` record so it can be:
  - Displayed in the Odoo UI
  - Returned to the client via the API

Usage:
    logger = ExecutionLogger(self)
    logger.info("Starting validation...")
    logger.ok("Checksum valid")
    logger.error("JAR failed")
    log = logger.get_log()   # str

All messages are simultaneously written to:
  1. The model's `execution_log` Text field (saved to DB)
  2. The standard Odoo server log via _logger
"""

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class ExecutionLogger:
    """Captures execution logs and stores them on a tds.validation record."""

    def __init__(self, record=None, initial_step=None):
        """
        Args:
            record: tds.validation record (optional, to persist logs).
            initial_step: optional initial message (e.g. "=== TDS Validation START ===").
        """
        self.record = record
        self._lines = []
        if initial_step:
            self._add_line(initial_step)

    # ── Logging helpers ──────────────────────────────────────────────────────

    def section(self, title):
        """Log a section heading with markers."""
        self._add_line(f"\n{'─' * 55}")
        self._add_line(f"  {title}")
        self._add_line(f"{'─' * 55}")

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

    # ── Persistence ──────────────────────────────────────────────────────────

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

    # ── Internal ─────────────────────────────────────────────────────────────

    def _add_line(self, line):
        """Add a timestamped line."""
        ts = datetime.now().strftime('%H:%M:%S')
        self._lines.append(f"[{ts}] {line}")

    def _rec_id(self):
        if self.record and self.record.id:
            return f"rec#{self.record.id}"
        return '?'
