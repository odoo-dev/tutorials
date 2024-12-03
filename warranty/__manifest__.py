{
   'name' : ' warranty',
   'version' : '1.0',
   'depends' : ['base','sale_management'],
   'author': "Author Name",
   'license':'LGPL-3',
   'description': 'Warranty management for products sold',

    'data' :[
        'security/ir.model.access.csv',
        'views/warranty_configuration_menu.xml',
        'views/warranty_configuration_view.xml',
        'wizard/warranty_wizard_view.xml',
        'views/sale_order_view.xml',
        'views/product_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
