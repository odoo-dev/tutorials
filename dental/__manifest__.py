{
    'name': "Dental App",
    'version': '1.0',
    'depends': ['base'],
    'description': """ Dental module """,
    'data': ['security/ir.model.access.csv',
             'views/dental_patient_view.xml',
             'views/dental_medical_aids_view.xml',
             'views/dental_chronic_condition_view.xml',
             'views/dental_allergy_view.xml',
             'views/dental_habit_view.xml',
             'views/dental_medication_view.xml',
             'views/dental_menu.xml'],
    'installable': True,
    'application': True,
    'sequence': -2,
    'license': 'LGPL-3'
}
