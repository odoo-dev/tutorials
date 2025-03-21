from odoo import http
from odoo.addons.sign.controllers.main import Sign

class SingInherit(Sign):

    def get_document_qweb_context(self, sign_request_id, token, **post):
        data = super().get_document_qweb_context(sign_request_id, token, **post)
        current_request_item = data['current_request_item']
        sign_item_types = data['sign_item_types']
        if current_request_item:
            for item_type in sign_item_types:
                if item_type['item_type'] == 'stamp':
                    signature_field_name = 'sign_stamp' 
                    user_signature = current_request_item._get_user_signature(signature_field_name)
                    user_signature_frame = current_request_item._get_user_signature_frame(signature_field_name)
                    item_type['auto_value'] = 'data:image/png;base64,%s' % user_signature.decode() if user_signature else False
                    item_type['frame_value'] = 'data:image/png;base64,%s' % user_signature_frame.decode() if user_signature_frame else False
        return data

    @http.route(["/sign/update_user_signature"], type="json", auth="user")
    def update_signature(self, sign_request_id, role, signature_type=None, datas=None, frame_datas=None):
        sign_request_item_sudo = http.request.env['sign.request.item'].sudo().search([('sign_request_id', '=', sign_request_id), ('role_id', '=', role)], limit=1)
        user = http.request.env.user
        allowed = sign_request_item_sudo.partner_id.id == user.partner_id.id
        if not allowed or signature_type not in ['sign_signature', 'sign_initials', 'sign_stamp'] or not user:
            return False
        user[signature_type] = datas[datas.find(',') + 1:]
        if frame_datas:
            user[signature_type+'_frame'] = frame_datas[frame_datas.find(',') + 1:]
        return True
