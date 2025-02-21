# -*- coding: utf-8 -*-
{
    'name': 'EasyWater Payment Authorize',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Payments',
    'summary': 'Authorize.Net to correctly use customer billing information.',
    'description': """
This module customizes the payment processing workflow with Authorize.Net:
- Ensures the customer’s billing information (instead of the logged-in internal user’s details) is sent to Authorize.Net.
Task-Id : 4499107
    """,
    'depends': ['payment_authorize'],
    'author': 'Odoo PS',
    'data': [],
    'installable': True,
    'license': 'LGPL-3',
}
