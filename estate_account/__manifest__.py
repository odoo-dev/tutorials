{
    "name": "estate_account",
    "author": "Odoo S.A.",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "estate", "account"],
    "license": "LGPL-3",
    # always loaded
    "data": [
        # 'security/ir.model.access.csv',
        "views/views.xml",
        "views/templates.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
