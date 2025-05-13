import base64
import logging
from odoo import http
from odoo.http import request


class CustomImageUpload(http.Controller):

    @http.route('/shop/upload_custom_image', type='json', auth='public', website=True, csrf=False)
    def upload_custom_image(self, line_id, image_base64, filename=None, mimetype=None):

        try:
            line = request.env['sale.order.line'].sudo().browse(int(line_id))
            if not line.exists():
                return {'error': 'Invalid line_id'}

            existing_attachment = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'sale.order.line'),
                ('res_id', '=', line.id),
                ('name', '=', filename),
            ], limit=1)
            if existing_attachment:
                existing_attachment.unlink()

            attachment = request.env['ir.attachment'].sudo().create({
                'name': filename or 'custom_image',
                'res_model': 'sale.order.line',
                'res_id': line.id,
                'type': 'binary',
                'mimetype': mimetype or 'image/png',
                'datas': image_base64,
                'public': False,
            })

            line.write({'custom_image': attachment.datas})

            return {'success': True}

        except Exception as e:
            return {'error': e}
