{
    'name': 'Stamp',
    'category': 'Sign/Stamp',
    'license': 'LGPL-3',
    'installable': True,
    'depends': ['sign'],
    'data': [
        "data/sign_data.xml",
        "views/sign_request_templates.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'sign_stamp/static/src/components/sign_request/*',
            'sign_stamp/static/src/dialogs/*',
        ],
        'sign.assets_public_sign': [
            'sign_stamp/static/src/components/sign_request/*',
            'sign_stamp/static/src/dialogs/*',
        ],
        'web.qunit_suite_tests': [
            'sign_stamp/static/tests/**/*',
        ],
    }
}
