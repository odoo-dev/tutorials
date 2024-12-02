
{

   'name' : ' Realestate',
   'version' : '1.0',
   'depends' : ['base','mail','website'],
   'author': "Author Name",
   'category': 'Real Estate/Brokerage',
   'license':'LGPL-3',
   'description': """
    Description text 
    """,

    'data' :[
        #security
        'security/security.xml',
        'security/ir.model.access.csv',
        # wizard view
        'wizard/estate_property_offer_wizard_view.xml',
        # website

        'views/estate_property_details.xml',
        'views/estate_property_website_view.xml',
    
        #views
        'views/menu_action.xml',
        'views/menu_view.xml',
        'views/estate_property_view.xml',
        'views/estate_property_types_view.xml',
        'views/estate_property_offer_view.xml',
        'views/estate_property_tag_view.xml',
        'views/res_users_view.xml',
        #reports and templates

        'report/company_details_template.xml',
        'report/offers_template.xml',
        'report/paper_formate.xml',
        'report/estate_property_templates.xml',    
        'report/estate_property_reports.xml',    
        'report/res_users_report_template.xml',
        'report/res_users_report.xml',

    ],
    'demo' :[
        'demo/estate.property.type.csv',
        'demo/estate_property_data.xml',
        'demo/estate_property_offer_data.xml',
        'demo/res_user_demo.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}



