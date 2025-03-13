{
    'name': 'Barcode Scan For PO/SO',
    'description': 'Allows to search product by barcode in Purchase Order and Sales Order',
    'depends': ['sale', 'purchase', 'sale_management', 'barcodes'],
    'assets': {
        'web.assets_backend': [
            'barcode_scan/static/src/js/barcode_scan_service.js',
            'barcode_scan/static/src/js/kanban_model.js',
            'barcode_scan/static/src/js/relational_model.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
}
