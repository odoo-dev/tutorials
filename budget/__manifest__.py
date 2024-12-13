{
    'name' :  'budget',
    'verion':'1.0',
    'license':'LGPL-3',
    'depends' : ['base','account','accountant'],
    'author': "njor",
    'data' :[
        'security/ir.model.access.csv',
        'views/budget_action.xml',
        'views/budget_menu_view.xml',
        'views/budget_line_view.xml',
        'views/budget_budget_view.xml',
        'views/budget_wizard_view.xml',
    ],
    'application':True,
    'installable': True,
    'auto_install': False 
}