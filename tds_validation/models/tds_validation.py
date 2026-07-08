import logging

from odoo import models, fields
from odoo.exceptions import UserError
from ..services.fvu_runner import FVURunner

_logger = logging.getLogger(__name__)


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
    tds_file = fields.Binary(string='TDS/TCS Input File (.txt)', required=True)
    tds_filename = fields.Char()
    challan_file = fields.Binary(string='Challan File (.csi)', required=True)
    challan_filename = fields.Char()
    consolidate_file = fields.Binary(string='Consolidate File (optional)')
    consolidate_filename = fields.Char()

    # ── Output ────────────────────────────────────────────────────
    output_attachment_ids = fields.Many2many(
        'ir.attachment',
        'tds_val_att_rel', 'val_id', 'att_id',
        string='Output Files', readonly=True
    )
    error_message = fields.Text(readonly=True)

    # ── Actions ───────────────────────────────────────────────────

    def action_run_validation(self):
        self.ensure_one()
        if self.state == 'running':
            raise UserError("Already running.")
        if not self.tds_file:
            raise UserError("Upload TDS/TCS Input File.")
        if not self.challan_file:
            raise UserError("Upload Challan File.")

        self.write({'state': 'running', 'error_message': False})
        self.env.cr.commit()  # show Running in UI immediately

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

            # Create attachments
            att_ids = []
            for f in outputs:
                att = self.env['ir.attachment'].create({
                    'name': f['name'],
                    'datas': f['b64'],
                    'res_model': self._name,
                    'res_id': self.id,
                    'description': 'TDS FVU Output',
                })
                att_ids.append(att.id)

            self.write({
                'state': 'done',
                'output_attachment_ids': [(6, 0, att_ids)],
            })
            self.message_post(body=f"✅ Validation complete. {len(att_ids)} file(s) attached.")

        except Exception as e:
            _logger.exception("TDS Validation failed [%s]", self.name)
            self.write({'state': 'failed', 'error_message': str(e)})
            self.message_post(body=f"❌ Failed: {e}")
            raise UserError(str(e)) from e
        finally:
            runner.cleanup()

    def action_reset(self):
        self.write({'state': 'draft', 'error_message': False})
