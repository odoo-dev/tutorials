{
    "name": "Budget Management",
    "version": "1.0",
    "depends": ["base", "account"],
    "author": "djip-odoo",
    "description": """
        Part of technical training
        Creating Budget Management module as review task
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/budget_line_views.xml",
        "wizards/actions_wizard.xml",
        "views/actions_menu_and_button.xml",
        "views/menu_views.xml",
        "views/budget_views.xml",
        'views/account_analytic_line_view.xml',
        "wizards/wizard_add_budgets_view.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
}
