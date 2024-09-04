{
    "name": "Dental",
    "Description": "Dental Module",
    "license": "LGPL-3",
    "summary": "Dental module for different purpose",
    "author": "Akpu_odoo",
    "version": "0.1",
    "application": True,
    "installable": True,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/dental_views.xml",
        "views/dental_menus.xml",
        "views/dental_patient_views.xml",
    ],
}
