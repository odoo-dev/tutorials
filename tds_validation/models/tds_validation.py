import logging
import os

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from ..services.fvu_runner import FVURunner
from ..services.version_checker import FVUVersionChecker
from ..services.log_service import ExecutionLogger

_logger = logging.getLogger(__name__)

VALID_TDS_EXTENSIONS = {'.txt', '.fvu'}
VALID_CSI_EXTENSION = '.csi'


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

    # ── Config ────────────────────────────────────────────────────
    @api.model
    def _get_jar_dir(self):
        """Read JAR directory from system parameters (single source of truth)."""
        return self.env['ir.config_parameter'].sudo().get_param(
            'tds_validation.jar_dir',
            '/home/odoo/Downloads/TDS_STANDALONE_FVU_9.4'
        )

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

    # ── Execution Log helpers ─────────────────────────────────────

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

    # ── Actions ───────────────────────────────────────────────────

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

        if self.state == 'running':
            elog.error('Already in Running state — cannot start again.')
            elog.persist(self)
            raise UserError('Already running.')

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
                elog.warn('Checksum provided but not yet validated against computed value')

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

        # ── 2. State → Running ──
        elog.section('Launching FVU Validation')
        elog.info('Setting state to Running...')
        self.write({'state': 'running', 'error_message': False})
        self.env.cr.commit()
        elog.persist(self)
        elog.ok('State set to Running')

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

        # Persist version info regardless of outcome
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

    def action_reset(self):
        self.write({
            'state': 'draft',
            'error_message': False,
            'execution_log': False,
            'fvu_version_local': False,
            'fvu_version_server': False,
            'fvu_version_status': 'unknown',
        })
