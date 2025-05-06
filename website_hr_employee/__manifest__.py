{
    'name': 'Website Employee',
    'category': 'Website/Website',
    'version': '0.1',
    'summary': 'Show Employees details in your website',
    'description': "This module allows to publish Employee details on your website",
    'depends': ['hr', 'website'],
    'data': [
        'views/snippets/s_employee_details.xml',
        'views/snippets/snippets.xml',
    ],
    'installable': True,
    'auto_install': ['hr', 'website'],
    'assets': {
        'web.assets_frontend': [
            'website_hr_employee/static/src/snippets/s_employee_details/000.js',
            'website_hr_employee/static/src/snippets/s_employee_details/000.xml',
        ],
        'website.assets_wysiwyg': [
            'website_hr_employee/static/src/snippets/s_employee_details/000.xml',
        ],
    },
    'author': 'Jay Panchal',
    'license': 'LGPL-3',
}
