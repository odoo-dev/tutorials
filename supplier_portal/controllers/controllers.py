from odoo import http
from odoo.http import request


class SupplierPortal(http.Controller):
    @http.route(['/sop_landing'], type='http', auth='public')
    def show_landing(self):
        return request.render('supplier_portal.landing')

    @http.route(['/supplier_portal/companies'], type='json', auth='user')
    def get_company_data(self, **kwargs):
        companies = request.env['res.company'].search([])
        company_list = []
        for company in companies:
            company_list.append({
                'id': company.id,
                'name': company.name
            })
        return company_list

    @http.route(['/supplier_portal/create_vendor_bill'], type='json', auth='user', methods=['POST'], csrf=True,)
    def create_vendor_bill(self, **kwargs):
        company_id = int(kwargs.get('company_id'))
        supplier = request.env.user.partner_id
        file = kwargs.get('file_data')
        bill = request.env['account.move'].sudo().create({
            'partner_id': supplier.id,
            'company_id': company_id,
            'move_type': 'in_invoice',
        })
        if file:
           data= request.env["ir.attachment"].sudo().create({
                "name": kwargs.get('file_name'),
                "type": "binary",
                "mimetype": 'application/pdf' if kwargs.get('file_name').endswith('.pdf') else 'text/xml',
                "datas": file,
                "res_model": "account.move",
                "res_id": bill.id,
            })
        return bill.id