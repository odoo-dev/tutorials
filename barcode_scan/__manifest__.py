{
    'name': 'Barcode Scan For PO/SO',
    'description': 'Allows to search product by barcode in Purchase Order and Sales Order',
    'depends': ['barcodes', 'purchase', 'sale', 'sale_management'],
    'assets': {
        'web.assets_backend': [
            'barcode_scan/static/src/**/*',
        ],
        'web.assets_unit_tests': [
            'barcode_scan/static/tests/**/*',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
}
