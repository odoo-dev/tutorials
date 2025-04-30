{
    "name": "Automated Real Estate Auction",
    'category': 'Real Estate/Brokerage',
    'depends': ['estate','account'],
    "data": [
            'views/cron.xml',
            'views/estate_property_views.xml',
            'views/estate_property_list.xml',
            'views/estate_property_details.xml',
            'views/offer_form_template.xml',
            'views/offer_success_template.xml',
            'views/mail_templates.xml',
    ],
    'auto-install': True,
    "application": True,
    "license": "LGPL-3",
    'assets': {
        'web.assets_backend': [
            'automated_real_estate_auction/static/src/js/status_of_property_form.js',
        ],
    },
}
