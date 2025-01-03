# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Standalone OWL App',
    'category': 'Odoo/Technical',
    'version': '1.0',
    'description': """
A simple OWL standalone To-Do app.
    """,
    'data': [
        'views/intro_view.xml',
    ],
    'assets': {
        'web.assets_backend_custom': [
            ("include", "web._assets_helpers"),
            ("include", "web._assets_backend_helpers"),
            ("include", "web._assets_primary_variables"),
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_functions.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            'web/static/lib/bootstrap/scss/_variables-dark.scss',
            'web/static/lib/bootstrap/scss/_maps.scss',
            ("include", "web._assets_bootstrap"),
            ("include", "web._assets_bootstrap_backend"),
            ('include', 'web._assets_core'),
            ("remove", "web/static/src/core/browser/router.js"),
            ("remove", "web/static/src/core/debug/**/*"),
            "web/static/src/libs/fontawesome/css/font-awesome.css",
            "web/static/src/views/fields/formatters.js",
            "web/static/lib/odoo_ui_icons/*",
            'owl_example/static/src/**/*',
        ],
    },
    'license': 'OEEL-1',
}
