{
    'name': 'Real Estate Auction',
    'version': '0.1',
    'summary': 'this will allow buyer to paricipate in auctions',
    'description': """
User can paricipate in auction and can create offers for the properties
    """,
    'author': 'Odoo',
    'depends': ['estate'],
    'data': [
        'views/estate_property_views.xml',
        'views/estate_property_offer_views.xml'
    ],
    'installable': True,
    'license': 'LGPL-3',
}