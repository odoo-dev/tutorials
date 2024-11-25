
{

   'name' : ' Realestate',
   'version' : '1.0',
   'depends' : ['base'],
   'author': "Author Name",
   'category': 'Category',
   'license':'LGPL-3',
   'description': """
    Description text 
    """,

    'data' :[
        #security
        'security/ir.model.access.csv',
        #views
        'views/menu_action.xml',
        'views/menu_view.xml',
        'views/estate_property_view.xml',
        'views/estate_property_types_view.xml',
        'views/estate_property_offer_view.xml',
        'views/estate_property_tag_view.xml',
        'views/res_users_view.xml',
        #data
        'data/master_data.xml',    
    ],
    'demo' :[
        'demo/estate.property.type.csv',
        'demo/estate_property_data.xml',
        'demo/estate_property_offer_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}



