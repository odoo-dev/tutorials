import hashlib
import base64
import logging
import requests
from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from ..services.fvu_runner import FVURunner

_logger = logging.getLogger(__name__)


class TdsValidation(models.Model):
    _name = 'tds.validation'
    _description = 'TDS FVU Validation'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True,
                       default=lambda self: (self.env['ir.sequence'].next_by_code('tds.validation') or 'New'))
    state = fields.Selection([('draft', 'Draft'),
                              ('queued', 'Queued'),
                              ('running', 'Running'),
                              ('done', 'Done'),
                              ('failed', 'Failed'),
                              ], default='draft', tracking=True)

    #  Input files
    tds_file = fields.Binary(string='TDS/TCS Input File', required=True, attachment=True,
                             help='Upload .txt or .fvu file')
    tds_filename = fields.Char(string='TDS Filename')

    csi_file = fields.Binary(string='Challan/Consolidate File (.csi)', attachment=True,
                             help='Upload .csi file for correction statements')
    csi_filename = fields.Char(string='CSI Filename')

    #  Client info
    db_instance_uuid = fields.Char(string='Client DB UUID', readonly=True)

    db_name = fields.Char(string='Client DB Name', readonly=True)

    company_name = fields.Char(string='Client Company', readonly=True)

    # Checksum
    checksum = fields.Char(string='Received Checksum', readonly=True,
                           help='SHA-256 checksum sent by the client for integrity verification')

    checksum_valid = fields.Boolean(string='Checksum Verified', readonly=True, default=False,
                                    help='Whether the received checksum matches the server-side computation')

    # Webhook / Async
    webhook_url = fields.Char(string='Client Webhook URL', readonly=True,
                              help='URL the client wants us to POST results back to after async processing')

    queued_date = fields.Datetime(string='Queued Date', readonly=True)

    processed_date = fields.Datetime(string='Processed Date', readonly=True)

    #  Reliability / Multi-user
    retry_count = fields.Integer(string='Retry Count', default=0, readonly=True,
                                 help='Number of times this record has been re-tried after getting stuck')

    webhook_delivered = fields.Boolean(string='Webhook Delivered', default=False,
                                       readonly=True, help='Whether the webhook callback was successfully delivered')

    last_webhook_attempt = fields.Datetime(string='Last Webhook Attempt', readonly=True,
                                           help='Last time we attempted to POST the webhook callback')

    webhook_attempt_count = fields.Integer(string='Webhook Attempt Count', default=0, readonly=True,
                                           help='Number of webhook delivery attempts made')

    # Output
    output_attachment_ids = fields.Many2many('ir.attachment', 'tds_val_att_rel', 'val_id',
                                             'att_id', string='Output Files', readonly=True)
    error_message = fields.Text(readonly=True)

    #  API / Integration fields
    is_api_request = fields.Boolean(string='API Request', default=False, help='Created via REST API')
    request_id = fields.Char(string='External Request ID', help='External reference from the calling system')

    # Static helpers

    @staticmethod
    def _compute_checksum(file_b64):
        """Compute SHA-256 hex digest of a base64-encoded file."""
        raw_bytes = base64.b64decode(file_b64)
        return hashlib.sha256(raw_bytes).hexdigest()

    @api.model
    def _get_config_int(self, key, default):
        """Read an integer config parameter."""
        val = self.env['ir.config_parameter'].sudo().get_param(key, str(default))
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    # Actions
    def action_process(self):
        self.ensure_one()

        if self.state == 'done':
            raise UserError(_('Already processed. Reset to draft to re-run.'))
        if self.state in ('queued', 'running'):
            raise UserError(_('Already queued. Wait for processing to complete.'))
        if self.state == 'failed':
            self.write({'state': 'draft', 'error_message': False})

        # Checksum verification
        if self.checksum:
            expected_checksum = self._compute_checksum(self.tds_file)
            if expected_checksum != self.checksum:
                _logger.error("Checksum mismatch for %s: expected=%s, received=%s", self.name, expected_checksum,
                              self.checksum)
                self.write({'state': 'failed',
                            'error_message': ('Checksum mismatch: file may be corrupted or ''tampered in transit.')})
                self.message_post(body=('❌ Checksum mismatch: file may be corrupted or ''tampered in transit.'))
                raise UserError(self.error_message)
            else:
                self.checksum_valid = True
        else:
            _logger.warning("No checksum provided for %s — skipping integrity check", self.name)

        #  Enqueue for background processing
        self.write({'state': 'queued', 'queued_date': fields.Datetime.now()})

    #  Cron processing
    @api.model
    def _cron_process_queued(self):

        batch_size = self._get_config_int('tds_validation.batch_size', 5)
        stuck_minutes = self._get_config_int('tds_validation.stuck_running_minutes', 10)
        max_retries = self._get_config_int('tds_validation.max_retries', 3)

        # Reclaim stuck running records
        stuck_threshold = fields.Datetime.now() - timedelta(minutes=stuck_minutes)
        stuck_records = self.search(
            [('state', '=', 'running'), ('write_date', '<', stuck_threshold.strftime('%Y-%m-%d %H:%M:%S'))])
        for rec in stuck_records:
            try:
                if rec.retry_count < max_retries:
                    rec.write({'state': 'queued',
                               'retry_count': rec.retry_count + 1
                               })
                    _logger.warning("Reclaimed stuck record %s (retry %d/%d)", rec.name, rec.retry_count, max_retries)
                else:
                    rec.write({'state': 'failed',
                               'error_message': 'Exceeded max retries after getting stuck.'
                               })
                    rec._send_webhook()
                    _logger.error("Record %s exceeded max retries — marked failed", rec.name)
            except Exception as e:
                _logger.exception("Error reclaiming stuck record %s: %s", rec.name, e)

        #  Fetch batch of queued records
        queued_records = self.search(
            [('state', '=', 'queued')],
            order='queued_date asc',
            limit=batch_size
        )
        _logger.info("_cron_process_queued: %d stuck reclaimed, processing %d queued record(s)", len(stuck_records),
                     len(queued_records))

        #  Process each record
        for record in queued_records:
            try:
                record._process_single()
            except Exception as e:
                _logger.exception("Unhandled error processing queued record %s: %s", record.name, e)

    def _process_single(self):

        self.ensure_one()

        #  Commit state='running' immediately (race-condition guard)
        self.write({'state': 'running'})
        self.env.cr.commit()

        jar_dir = '/home/odoo/Downloads/TDS_STANDALONE_FVU_9.4'
        runner = FVURunner(self.id, jar_dir)

        try:
            outputs = runner.run(tds_b64=self.tds_file,
                                 tds_filename=self.tds_filename,
                                 csi_b64=self.csi_file or None,
                                 csi_filename=self.csi_filename or None,
                                 )

            # Create attachments
            att_ids = []
            for f in outputs:
                att = self.env['ir.attachment'].create({'name': f['name'],
                                                        'datas': f['b64'],
                                                        'res_model': self._name,
                                                        'res_id': self.id,
                                                        'description': 'TDS FVU Output',
                                                        })
                att_ids.append(att.id)

            self.write({
                'state': 'done',
                'error_message': False,
                'output_attachment_ids': [(6, 0, att_ids)],
                'processed_date': fields.Datetime.now(),
                'checksum_valid': self.checksum_valid,
            })

            self.message_post(body=f"✅ Validation complete. {len(att_ids)} output file(s) attached.")

        except Exception as e:
            _logger.exception("TDS validation failed [%s]: %s", self.name, e)
            self.write({
                'state': 'failed',
                'error_message': str(e),
                'processed_date': fields.Datetime.now(),
            })
            self.message_post(body=f"❌ Validation failed: {e}")

        finally:
            runner.cleanup()
            self.env.cr.commit()

        #  Send webhook after state is finalised
        self._send_webhook()

    #  Webhook delivery
    def _send_webhook(self):
        self.ensure_one()

        now = fields.Datetime.now()
        self.write({
            'last_webhook_attempt': now,
            'webhook_attempt_count': self.webhook_attempt_count + 1,
        })

        if not self.webhook_url:
            _logger.warning(
                "No webhook URL for %s — skipping webhook callback",
                self.name,
            )
            return

        is_success = self.state == 'done'
        payload = {
            'jsonrpc': '2.0',
            'params': {
                'validation_id': self.id,
                'reference': self.name,
                'status': 'ok' if is_success else 'error',
                'message': self.error_message or 'processed',
                'output_files': [
                    {'name': a.name, 'b64': a.datas.decode()}
                    for a in self.output_attachment_ids
                ] if is_success else [],
            },
        }

        _logger.info("Sending webhook to %s for %s (status=%s, attempt=%d)", self.webhook_url, self.name,
                     payload['params']['status'], self.webhook_attempt_count)

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=15)
            resp.raise_for_status()
            self.write({'webhook_delivered': True})
            _logger.info("Webhook to %s succeeded (HTTP %d)", self.webhook_url, resp.status_code)
        except Exception as e:
            _logger.error("Webhook to %s failed for %s (attempt %d): %s", self.webhook_url, self.name,
                          self.webhook_attempt_count, e)

    @api.model
    def _cron_retry_webhooks(self):
        max_webhook_retries = 3
        retry_threshold = fields.Datetime.now() - timedelta(minutes=5)

        records = self.search([
            ('state', 'in', ('done', 'failed')),
            ('webhook_delivered', '=', False),
            ('webhook_attempt_count', '<', max_webhook_retries),
            '|',
            ('last_webhook_attempt', '=', False),
            ('last_webhook_attempt', '<', retry_threshold.strftime('%Y-%m-%d %H:%M:%S')),
        ])

        _logger.info("_cron_retry_webhooks: found %d record(s) needing webhook retry", len(records))

        for rec in records:
            try:
                rec._send_webhook()
            except Exception as e:
                _logger.exception("Unhandled error retrying webhook for %s: %s", rec.name, e)

    def action_resend_webhook(self):
        """
        Manual button: resend webhook for a finished record.
        """
        self.ensure_one()
        if self.state not in ('done', 'failed'):
            raise UserError(_('Nothing to resend until processing is finished (done or failed).'))
        self._send_webhook()

    def action_reset(self):
        """Reset failed record back to draft for re-processing."""
        self.write({
            'state': 'draft',
            'error_message': False
        })
