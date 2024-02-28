{
    'name': "Estate",
    'version': '1.0',
    'depends': ['base', 'mail'],
    'author': "jeep-odoo",
    'category': 'Real Estate/Brokerage',
    'data': [
        'security/estate_security.xml',
        'security/ir.model.access.csv',
        'wizard/offer_entry_wizard_views.xml',
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/inherited_res_user_views.xml',
        'report/estate_property_templates.xml',
        'report/estate_property_reports.xml',
        'views/estate_menus.xml',
    ],
    'demo':[
        'demo/estate.property.type.csv',
        'demo/demo_data.xml'
    ],
    'application': True,
    'installable': True,
    "license" : "LGPL-3",
}
