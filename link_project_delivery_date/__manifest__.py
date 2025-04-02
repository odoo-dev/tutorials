{
    'name': "Link Project Delivery Date with analytical acounting",
    'summary': "Link project delivery date with recognition date associated to each journal items with the analytical account of that project",
    'depends': [
        'sale_project', 'accountant'
    ],
    'data': [
        'views/project_project_views.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',
}
