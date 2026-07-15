"""
TDS Validation Model
--------------------
Multi-user background queue processing for FVU JAR validation.
State machine: draft → queued → running → done | failed
Queue processed by ir.cron — supports multiple concurrent users
without blocking Odoo workers.
"""

import logging
import os

import requests

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from ..services.fvu_runner import FVURunner
from ..services.version_checker import FVUVersionChecker
from ..services.log_service import ExecutionLogger

_logger = logging.getLogger(__name__)

VALID_TDS_EXTENSIONS = {'.txt', '.fvu'}
VALID_CSI_EXTENSION = '.csi'

MAX_CONCURRENT_DEFAULT = 2


class TdsValidation(models.Model):
    _name = 'tds.validation'
    _description = 'TDS FVU Validation'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Reference', required=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('tds.validation') or 'New'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft', tracking=True)

    # ── Input files ───────────────────────────────────────────────
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

    # ── Output ────────────────────────────────────────────────────
    output_attachment_ids = fields.Many2many(
        'ir.attachment',
        'tds_val_att_rel', 'val_id', 'att_id',
        string='Output Files', readonly=True
    )
    error_message = fields.Text(readonly=True)

    # ── API / Integration fields ───────────────────────────────────
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
    webhook_url = fields.Char(
        string='Webhook URL',
        help='URL to POST the validation results to when complete'
    )
    webhook_sent = fields.Boolean(
        string='Webhook Sent',
        default=False,
        help='Whether webhook notification has been sent'
    )

    # ── Execution log ──────────────────────────────────────────────
    execution_log = fields.Text(
        string='Execution Log',
        readonly=True,
        help='Full step-by-step log of the validation execution'
    )

    # ── FVU version tracking ──────────────────────────────────────
    fvu_version_local = fields.Char(string='Local FVU Version', readonly=True)
    fvu_version_server = fields.Char(string='Server FVU Version', readonly=True)
    fvu_version_status = fields.Selection([
        ('unknown', 'Unknown'),
        ('current', 'Up-to-date'),
        ('warn', 'Minor outdated'),
        ('old', 'Old'),
        ('unverified', 'Unverified'),
    ], string='FVU Version Status', default='unknown', readonly=True)

    # ── Queue tracking ────────────────────────────────────────────
    queued_at = fields.Datetime(
        string='Queued At',
        readonly=True,
        help='When this record was added to the processing queue'
    )
    processing_started_at = fields.Datetime(
        string='Processing Started At',
        readonly=True,
        help='When the FVU JAR actually started running'
    )

    # ── Config ────────────────────────────────────────────────────
    @api.model
    def _get_jar_dir(self):
        """Read JAR directory from system parameters."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'tds_validation.jar_dir',
            '/home/odoo/Downloads/TDS_STANDALONE_FVU_9.4'
        )

    @api.model
    def _get_max_concurrent(self):
        """Max number of validations that can run simultaneously."""
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'tds_validation.max_concurrent',
            str(MAX_CONCURRENT_DEFAULT)
        ))

    # ── Validation ────────────────────────────────────────────────

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

    # ── Actions ───────────────────────────────────────────────────

    def action_queue_validation(self):
        """
        Pre-validate files and add to processing queue.
        Called when user clicks "▶ Queue Validation" or
        when API receives a generate request.
        
        Returns immediately — JAR runs in background via cron.
        """
        self.ensure_one()

        # ── Init logger ──
        elog = ExecutionLogger(
            self,
            initial_step=f"=== TDS Validation QUEUED — {self.name} ===",
        )
        elog.detail('Validation ID', self.id)
        elog.detail('Request ID', self.request_id or 'N/A')
        if self.webhook_url:
            elog.detail('Webhook URL', self.webhook_url)

        if self.state == 'running':
            elog.error('Already in Running state.')
            elog.persist(self)
            raise UserError('Already running.')
        if self.state == 'queued':
            elog.error('Already in queue.')
            elog.persist(self)
            raise UserError('Already queued.')

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

        # ── Checksum validation (if provided) ──
        if self.checksum:
            elog.section('Checksum Verification')
            elog.detail('Provided checksum', self.checksum)
            if self.checksum_valid:
                elog.ok('Checksum matched — data integrity verified')
            else:
                elog.warn('Checksum provided but not yet validated')

        # ── Version check before queuing ──
        try:
            self._check_fvu_version(elog)
        except (UserError, ValidationError):
            elog.persist(self)
            raise
        except Exception:
            elog.error('Version check failed unexpectedly')
            elog.persist(self)
            raise

        elog.info('Adding to background processing queue...')
        elog.persist(self)

        # ── Check slot BEFORE writing state (avoid flush on non-existent column) ──
        can_start = self._try_claim_slot()

        # ── Set state = queued ──
        self.write({
            'state': 'queued',
            'error_message': False,
            'execution_log': elog.get_log(),
            'queued_at': fields.Datetime.now(),
        })
        self.env.cr.commit()  # Commit so other workers/cron can see this record

        if can_start:
            # Slot available — start processing right away
            self._execute_validation()
        else:
            self.message_post(
                body=(
                    f"⏳ Validation queued at position "
                    f"#{self._queue_position()}. "
                    f"Processing will start shortly."
                )
            )

    @api.model
    def action_process_queue(self):
        """
        Cron job entry point.
        Picks queued records and processes them (max concurrent limit).
        Runs every 30 seconds via ir.cron.
        """
        max_concurrent = self._get_max_concurrent()
        running_count = self.search_count([('state', '=', 'running')])

        if running_count >= max_concurrent:
            _logger.info(
                "Queue: %d running (max %d) — skipping this tick",
                running_count, max_concurrent
            )
            return

        slots = max_concurrent - running_count
        queued = self.search(
            [('state', '=', 'queued')],
            order='create_date asc',
            limit=slots,
        )

        if not queued:
            return

        _logger.info(
            "Queue: processing %d of %d queued records (running=%d, max=%d)",
            len(queued), self.search_count([('state', '=', 'queued')]),
            running_count, max_concurrent
        )

        for record in queued:
            try:
                record._execute_validation()
            except Exception as e:
                _logger.exception(
                    "Queue processing failed for %s", record.name
                )
                record.write({
                    'state': 'failed',
                    'error_message': str(e),
                })
                self.env.cr.commit()

    def _try_claim_slot(self):
        """
        Check if a concurrent slot is available and claim it.
        Returns True if slot claimed (processing can start immediately),
        False if queued (wait for cron).
        """
        max_concurrent = self._get_max_concurrent()
        running_count = self.search_count([
            ('state', '=', 'running'),
            ('id', '!=', self.id),
        ])
        return running_count < max_concurrent

    def _queue_position(self):
        """Return the position of this record in the queue."""
        older = self.search_count([
            ('state', '=', 'queued'),
            ('create_date', '<', self.create_date),
        ])
        return older + 1

    def _execute_validation(self):
        """
        Actual JAR execution (called from action_process_queue
        or directly if slot available).
        """
        self.ensure_one()

        elog = ExecutionLogger(
            self,
            initial_step=f"=== TDS Validation START — {self.name} ===",
        )
        elog.detail('Validation ID', self.id)
        elog.detail('Request ID', self.request_id or 'N/A')
        if self.webhook_url:
            elog.detail('Webhook URL', self.webhook_url)
        elog.persist(self)

        # ── Log checksum status ──
        if self.checksum:
            elog.section('Checksum Verification')
            elog.detail('Provided checksum', self.checksum)
            if self.checksum_valid:
                elog.ok('Checksum matched — data integrity verified')
            else:
                elog.warn('Checksum provided but not yet validated against computed value')

        # ── Set state = running ──
        elog.section('Launching FVU Validation')
        elog.info('Setting state to Running...')
        self.write({
            'state': 'running',
            'error_message': False,
            'processing_started_at': fields.Datetime.now(),
        })
        self.env.cr.commit()
        elog.persist(self)
        elog.ok('State set to Running')

        # ── Run JAR ──
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

            # ── Send webhook (if configured) ──
            if self.webhook_url and not self.webhook_sent:
                self._send_webhook(outputs, elog)

        except Exception as e:
            elog.error(f'Validation failed: {e}')
            elog.persist(self)
            _logger.exception("TDS Validation failed [%s]", self.name)
            self.write({'state': 'failed', 'error_message': str(e)})
            self.message_post(body=f"❌ Failed: {e}")

            # Send webhook with failure state
            if self.webhook_url and not self.webhook_sent:
                self._send_webhook([], elog, error=str(e))

            raise UserError(str(e)) from e
        finally:
            runner.cleanup()
            try:
                if not self.execution_log:
                    elog.persist(self)
            except Exception:
                pass

    def action_reset(self):
        """Reset failed/queued record back to draft."""
        self.write({
            'state': 'draft',
            'error_message': False,
            'execution_log': False,
            'webhook_sent': False,
            'fvu_version_local': False,
            'fvu_version_server': False,
            'fvu_version_status': 'unknown',
            'queued_at': False,
            'processing_started_at': False,
        })

    def _send_webhook(self, output_files, elog, error=None):
        """POST validation results to the configured webhook URL (JSON-RPC)."""
        webhook_url = self.webhook_url
        if not webhook_url:
            return

        elog.section('Webhook Callback')
        elog.detail('Webhook URL', webhook_url)
        elog.info('Sending results via webhook...')

        payload = {
            'event': 'validation.complete',
            'validation_id': self.id,
            'reference': self.name,
            'state': self.state,
            'request_id': self.request_id or '',
            'checksum': self.checksum or '',
            'checksum_valid': self.checksum_valid,
            'execution_log': self.execution_log or '',
            'error_message': self.error_message or '',
            'error': error or '',
            'output_files': output_files,
        }

        try:
            resp = requests.post(
                webhook_url,
                json={'jsonrpc': '2.0', 'params': payload},
                timeout=60,
            )
            if resp.status_code == 200:
                try:
                    resp.json()
                    elog.ok(f'Webhook sent successfully (HTTP {resp.status_code})')
                except Exception:
                    elog.warn(f'Webhook returned HTTP {resp.status_code} (non-JSON body)')
            else:
                elog.warn(f'Webhook returned HTTP {resp.status_code}: {resp.text[:200]}')
        except Exception as e:
            elog.warn(f'Webhook failed: {e}')
        finally:
            self.write({'webhook_sent': True})
            elog.persist(self)

    def _check_fvu_version(self, elog=None):
        """Version check matching test.sh logic."""
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

        _logger.info(
            'FVU Version Check — Status: %s | Local: %s | Server: %s | %s',
            result['status'], result['local_version'],
            result.get('server_version', 'N/A'), result['message'],
        )

        status_map = {
            'error': 'unverified',
            'old': 'old',
            'warn': 'warn',
            'current': 'current',
        }

        self.write({
            'fvu_version_local': result['local_version'],
            'fvu_version_server': result.get('server_version', ''),
            'fvu_version_status': status_map.get(result['status'], 'unknown'),
        })

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
