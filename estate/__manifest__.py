
{

   'name' : ' Realestate',
   'version' : '1.0',
   'depens' : ['base'],
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
        'views/estate_property_form_view.xml',
        'views/estate_property_search_view.xml',
        'views/estate_property_types_view.xml',
        'views/estate_property_offer_form_view.xml',
        'views/estate_property_offer_list_view.xml',
        'views/estate_property_tag_view.xml',
        'views/res_users_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}



