
{
    'name': 'Real Estate',
    'version': '1.0',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv', 
        'views/res_user_views.xml', 
        'views/estate_property_offer_views.xml', 
        'views/estate_property_views.xml', 
        'views/estate_property_type_views.xml', 
        'views/estate_property_tag_views.xml', 
        'views/estate_menus.xml', 
        'data/master_data.xml', 
        # 'report/estate_property_templates.xml',    
        # 'report/estate_property_reports.xml',    
    ],
    'demo': [
        'demo/estate.property.type.csv',
        'demo/estate_property_data.xml',
        'demo/estate_property_offer_data.xml', 
    ],
    'installable': True,
    'application': True,
}
