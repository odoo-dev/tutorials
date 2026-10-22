# -*- coding: utf-8 -*-

import logging
import random

from odoo import http
from odoo.http import request

logger = logging.getLogger(__name__)

class AwesomeDashboard(http.Controller):
    @http.route('/awesome_dashboard/statistics', type='jsonrpc', auth='user')
    def get_statistics(self):
        """Return the order statistics displayed as dashboard cards."""
        return [
            {
                'label': 'New orders this month',
                'value': random.randint(10, 200),
            },
            {
                'label': 'Total amount this month',
                'value': random.randint(100, 1000),
            },
            {
                'label': 'Average t-shirts per order this month',
                'value': random.randint(4, 12),
            },
            {
                'label': 'Cancelled orders this month',
                'value': random.randint(0, 50),
            },
            {
                'label': 'Average time from new to sent or cancelled (hours)',
                'value': random.randint(4, 123),
            },
        ]

