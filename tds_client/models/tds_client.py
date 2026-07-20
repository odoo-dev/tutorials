from odoo import models, fields, api

import logging
import os

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

VALID_TDS_EXTENSIONS = {'.txt', '.fvu'}
VALID_CSI_EXTENSION = '.csi'


class TdsClient(models.Model):
    _name = 'tds.client'
    _description = 'TDS Validation Client'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', required=True, default='New')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sending', 'Sending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ], default='draft', tracking=True)

    # Input files
    tds_file = fields.Binary(
        string='TDS/TCS Input File',
        required=True,
        attachment=True,
        help='Upload .txt or .fvu file'
    )
    tds_filename = fields.Char(string='Filename')

    csi_file = fields.Binary(
        string='Challan File (.csi)',
        attachment=True,
        help='Upload .csi file for correction statements'
    )
    csi_filename = fields.Char(string='CSI Filename')

    # ── Database identification
    db_instance_uuid = fields.Char(
        string='Database Instance UUID',
        readonly=True, copy=False,
        default=lambda self: self._default_db_instance_uuid(),
        help='Odoo database instance UUID (from ir.config_parameter)'
    )

    db_name = fields.Char(
        string='Database Name',
        readonly=True, copy=False,
        default=lambda self: self._default_db_name(),
        help='PostgreSQL database name'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True, copy=False,
        default=lambda self: self.env.company,
        help='Company this record belongs to'
    )

    @api.model_create_multi
    def create(self, vals_list):
        # logging.warning("checking the create method call ")
        for rec in vals_list:
            rec['name'] = self.env['ir.sequence'].next_by_code('tds.client')
        return super().create(vals_list)

    @api.model
    def _default_db_instance_uuid(self):
        return self.env['ir.config_parameter'].sudo().get_param('database.uuid', '')

    @api.model
    def _default_db_name(self):
        return self.env.cr.dbname

    # ── Validation helpers
    @staticmethod
    def _is_valid_tds_name(name):
        # splitext use for split the file name in two parts like tds.txt ("tds",".txt")
        # ( _ ) is used for file store in variable, but we don't want so we assign in underscore
        _, ext = os.path.splitext(name.lower())
        return ext in VALID_TDS_EXTENSIONS

    @staticmethod
    def _is_valid_csi_name(name):
        return name.lower().endswith(VALID_CSI_EXTENSION)

    @api.onchange('tds_filename')
    def onchange_tds_file(self):
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            self.tds_file = False
            self.tds_filename = ""
            return {
                'warning': {
                    'title': 'Invalid TDS filename',
                    'message': 'TDS file must end with .txt or .fvu',
                }
            }

    @api.onchange('csi_filename')
    def onchange_csi_filename(self):
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            self.csi_file = False
            self.csi_filename = ""
            return {
                'warning': {
                    'title': 'Invalid CSI filename',
                    'message': 'Challan file must end with .csi',
                }
            }

    # ── Actions
    def action_send_to_server(self):
        self.ensure_one()
        # ── Pre-flight checks ──
        if self.state == 'sending':
            raise UserError('Request already in progress.')
        if not self.tds_file:
            raise UserError('Upload TDS/TCS Input File.')
        if self.tds_filename and not self._is_valid_tds_name(self.tds_filename):
            raise UserError('TDS file must end with .txt or .fvu')
        if self.csi_filename and not self._is_valid_csi_name(self.csi_filename):
            raise UserError('Challan file must end with .csi')

        self.write({
            'state': 'sending',
        })
        self.env.cr.commit()
        # logging.warning("Button Clicked ")

    def action_reset(self):
        self.write({
            'state': 'draft',
        })
