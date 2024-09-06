{
    'name': 'Dental',
    'version': '17.0',
    'summary': 'Manage Dental Patients , Appointments and Medical Record',
    'author': 'Your Name',
    'depends': ['base', 'mail', 'account'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/dental_medical_aids_view.xml',
        'views/dental_template.xml',
        'views/dental_patient_views.xml',
        'views/dental_medical_symptoms_view.xml',
        'views/dental_medication_views.xml',
        'views/dental_chronic_conditions_views.xml',
        'views/dental_allergies_view.xml',
        'views/dental_habits_view.xml',
        'views/dental_configuration_views.xml',
        'views/dental_medical_history_view.xml',
        'views/dental_patient_menus.xml'
    ],
    'installable': True,
    'application': True,
}
