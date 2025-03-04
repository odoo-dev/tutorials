{
    'name' : "Real Estate Auction",
    'summary' : "A module adding auction functionality to real estate management in Odoo.",
    'author': "Krunal Gelot",
    'website': "https://www.odoo.com",
    'category': 'Tutorials',
    'version': '0.1',
    'depends': ['estate', 'website', 'mail'],
    'application': False,
    'installable': True,
    'data':[
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml'
    ],
    'license': 'AGPL-3'
}
