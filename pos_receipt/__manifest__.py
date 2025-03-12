{
    'name': 'POS Receipt',
    'depends': ['point_of_sale'],
    'data': [
        "views/res_config_settings_form_inherit.xml",
        "wizard/pos_receipt_layout.xml",
        "wizard/pos_receipt_layout_preview.xml",
        "security/ir.model.access.csv",
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_receipt/static/src/**/*',
            'point_of_sale/static/src/**/*'
          
        


           
        ],

        'point_of_sale.receipt_assets_lazy': [
            ('include', 'web.assets_backend_lazy'),
            'pos_receipt/static/src/receipt/order_receipt_inherit.js',
            'pos_receipt/static/src/receipt/order_receipt_inherit.xml',
            'pos_receipt/static/src/receipt/receipt_header/*',
            'point_of_sale/static/src/app/generic_components/orderline/orderline.js',
            'point_of_sale/static/src/app/generic_components/order_widget/order_widget.js',
            'point_of_sale/static/src/app/screens/receipt_screen/receipt/receipt_header/receipt_header.js',
            'point_of_sale/static/src/app/generic_components/centered_icon/centered_icon.js',
            'point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.js',
            'point_of_sale/static/src/utils.js', 
            'point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',
            'point_of_sale/static/src/app/screens/receipt_screen/receipt/receipt_header/*', 
            

        
        ],

        'web.assets_backend': [
        'pos_receipt/static/src/receipt_preview_iframe.js',
        
        
   
        ],
           'point_of_sale.receipt_assets': [
            ('include', 'web.assets_frontend'),
              'web/static/fonts/fonts.scss',
              'pos_receipt/static/src/receipt/css/pos_receipts.css'

        ],  
    },

    'license': 'LGPL-3',
}