{
    'name': "Stock Transport",
    'version': '1.0',
    'depends': ['stock_picking_batch', 'fleet', 'web_gantt'],
    'author': "Rajat",
    'description': """ Description text""",
    'data': [
        'security/stock_transport_groups.xml',
        'security/ir.model.access.csv',
        'views/fleet_vehicle_model_views.xml',
        'views/stock_picking_batch_views.xml',
        'views/stock_picking_views.xml'
    ],
    'application': False,
    'installable': True
}
