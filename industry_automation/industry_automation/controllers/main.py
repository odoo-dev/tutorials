from odoo import http
from odoo.http import request
import base64

class IndustryAutomationController(http.Controller):

    @http.route('/industry_automation/upload', type='http', auth='user', website=True)
    def upload_page(self, **kw):
        return request.render('industry_automation.upload_template', {})

    @http.route('/industry_automation/upload_file', type='http', auth='user', website=True, csrf=False)
    def upload_file(self, **post):
        dump_file = post.get('db_file')
        if dump_file:
            filename = dump_file.filename
            if not filename.lower().endswith('.zip'):
                return request.render('industry_automation.upload_template', {
                    'error': True,
                    'error_msg': 'Only ZIP files are allowed.'
                })

            file_data = dump_file.read()

            project_id = request.env['ir.config_parameter'].sudo().get_param('industry_automation.project_id')
            if project_id:
                # Create the task
                task = request.env['project.task'].sudo().create({
                    'name': f'New Dump File Uploaded: {filename}',
                    'description': 'Dump DB File Uploaded via Web Form',
                    'project_id': int(project_id),
                })

                # Create attachment and link to the task
                request.env['ir.attachment'].sudo().create({
                    'name': filename,
                    'datas': base64.b64encode(file_data),
                    'res_model': 'project.task',
                    'res_id': task.id,
                    'type': 'binary',
                    'mimetype': dump_file.content_type,
                })

                return request.render('industry_automation.upload_template', {
                    'success': True,
                    'filename': filename
                })

        return request.render('industry_automation.upload_template', {
            'error': True,
            'error_msg': 'Something went wrong. Please try again.'
        })

