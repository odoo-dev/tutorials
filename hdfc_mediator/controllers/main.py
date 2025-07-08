from odoo import http
from odoo.http import Response
import requests
import json

class HDFCMediatorController(http.Controller):

    @http.route('/hdfc/statement', type='jsonrpc', auth='public', methods=['POST'], csrf=False)
    def get_statement(self, **kwargs):
        data = kwargs.get('data')
        print(data)
        hdfc_url = 'https://dummyjson.com/todos'  # Dummy API

        try:
            res = requests.get(hdfc_url)
            res.raise_for_status()
            return {
                "jsonrpc": "2.0",
                "id": None,
                "result": res.json()
            }
        except requests.RequestException as e:
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                content_type='application/json'
            )


    # @http.route('/hdfc/statements', type='json', auth='public', methods=['POST'], csrf=False)
    # def get_statements(self, **payload):
    #     """
    #     This endpoint receives JSON payload from the client,
    #     forwards it to the HDFC API (dummy for now),
    #     and returns the response in JSON-RPC format.
    #     """
    #     hdfc_url = 'https://httpbin.org/post'  # Replace with actual HDFC endpoint

    #     try:

    #         # Send request to HDFC API
    #         response = requests.post(hdfc_url, json=payload, timeout=30)
    #         response.raise_for_status()

    #         # Parse JSON response
    #         hdfc_data = response.json()

    #         # Return JSON-RPC style response
    #         return {
    #             "jsonrpc": "2.0",
    #             "id": None,
    #             "result": hdfc_data
    #         }

    #     except requests.RequestException as e:
    #         return {
    #             "jsonrpc": "2.0",
    #             "id": None,
    #             "error": {
    #                 "code": 500,
    #                 "message": "Failed to reach HDFC API",
    #                 "data": str(e)
    #             }
    #         }