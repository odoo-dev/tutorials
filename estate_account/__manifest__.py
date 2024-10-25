{
    'name': "Real Estate Account",
    'version': '1.0',
    'depends': ['account', 'estate'],
    'author': "Ayushmaan",
    'category': 'Account',
    'description': """
    Second Application
    """,
    # data files always loaded at installation
    'data': [
        'report/estate_account_property_invoice.xml'
    ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    'installable': True,
    'application': False
}
