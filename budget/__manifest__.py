{
    "name": "Budget",
    "version": "1.0",
    "depends": ["base", "account"],
    "data": [
        "wizard/budget_wizard_views.xml",
        "views/budget_lines_views.xml",
        "views/budget_views.xml",
        "views/budget_menus.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}