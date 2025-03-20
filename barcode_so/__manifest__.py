{
    'name': 'Barcode Scan For PO/SO',
    'description': 'Allows to search product by barcode in Purchase Order and Sales Order',
    'depends': ['sale', 'purchase', 'sale_management', 'barcodes'],
    'assets': {
        'web.assets_backend': [
            'barcode_so/static/src/js/barcode_scan_service.js',
            'barcode_so/static/src/js/kanban_model.js',
            'barcode_so/static/src/js/relational_model.js',
        ],
        'web.assets_unit_tests': [
            'barcode_so/static/tests/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
}
