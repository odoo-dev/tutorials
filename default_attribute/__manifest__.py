# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Default_Attribute",
    'summary': "Default attribute on product configurator",
    'author': "Odoo",
    'website': "https://www.odoo.com",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['stock', 'sale_management'],
    'license': "LGPL-3",
    'data': [
        'security/ir.model.access.csv',
        'views/view_category_property_form_stock.xml',
        'views/sale_order_view.xml',
    ],
}

