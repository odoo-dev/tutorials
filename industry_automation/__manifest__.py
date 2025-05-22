{
    'name': 'Industry Automation',
    'version': '1.0',
    'summary': 'Industry Automation Cleanup',
    'author': 'chirag Gami(chga)',
    'category': 'Automation',
    'depends': ['base', 'project'],
    'license': 'LGPL-3',
    'data': [
        'views/project_task_views.xml',
        'data/fetch_db_cron.xml',
    ],
    'installable': True,
    'application': True,
}
