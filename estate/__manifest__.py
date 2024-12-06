
{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Real Estate/Brokerage',
    'depends': [
        'base',
    ],
    'data': [
        'security/security.xml', 
        'security/ir.model.access.csv', 
        'views/res_user_views.xml', 
        'wizard/estate_property_offer_wizard_view.xml',
        'views/estate_property_offer_views.xml', 
        'views/estate_property_views.xml', 
        'views/estate_property_type_views.xml', 
        'views/estate_property_tag_views.xml', 
        'views/estate_menus.xml', 
        'data/master_data.xml',
        'report/estate_property_templates.xml',    
        'report/estate_property_offer_templates.xml',    
        'report/estate_property_reports.xml',
        'report/res_users_templates.xml',   
        'report/res_users_reports.xml'    
    ],
    'demo': [
        'demo/estate.property.type.csv',
        'demo/estate_property_data.xml',
        'demo/estate_property_offer_data.xml', 
    ],
    'installable': True,
    'application': True,
    "license": "LGPL-3",
}
