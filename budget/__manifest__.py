{
    'name' :  'budget',
    'license':'LGPL-3',
    'depends' : ['base','account'],
    'author': "njor",
    'data' :[
        'security/ir.model.access.csv',
        'views/budget_line_view.xml',
        'views/budget_budget_view.xml',
        'views/budget_action.xml',
        'views/budget_menu_view.xml',
        'views/budget_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False 
}