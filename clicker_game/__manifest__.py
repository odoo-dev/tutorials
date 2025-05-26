{
    'name': "Clicker Game",
    'author': "Odoo",
    'website': "https://www.odoo.com/",
    'version': '1.0',
    'application': False,
    'installable': True,
    'depends': ['base', 'web', 'mail'],
    'assets': {
        'web.assets_backend': [
            'clicker_game/static/src/**/**/*',
        ],
    },
    'license': 'LGPL-3'
}
