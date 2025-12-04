# case study: reports
{
    'name': 'ext_casestudy_report',
    'depends': ['base', 'account'],
    'application': False,
    'installable': True,
    'data': [
        'report/contact_reports.xml',
        'report/contact_templates.xml',
        'report/report_invoice.xml'
    ]
}