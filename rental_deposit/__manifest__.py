# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "rental_deposit",
    'description': """
Deposit for rental contracts
    """,
    'author': "Odoo",
    'website': "https://www.odoo.com",
    'license': 'LGPL-3',
    'category': 'Customizations',
    'version': '0.1',
    'depends': ['sale_renting'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/res_config_settings_view.xml',
    ],
}

