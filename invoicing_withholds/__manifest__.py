{
    'name' : 'Import Withholds',
    'description' : 'Import withholdings from XLS file and apply to invoices',
    'version' : '0.1',
    'category' : 'Accounting/Localizations/EDI',
    'author' : 'ssud',
    'depends' : [ "account", "l10n_ec_edi" ],
    'data' : [
        "security/ir.model.access.csv",
        "views/import_withhold_views.xml",
    ],
    'application' : False,
    'installable' : True,
    'license' : 'LGPL-3',
}
