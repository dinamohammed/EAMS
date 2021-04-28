# -*- coding: utf-8 -*-
{
    'name': "Budget Purchase Relation",

    'summary': """
        Relate Budgets with Purchase Orders""",

    'description': """
    """,

    'author': "Egymentors",
    'website': "http://www.egymentors.com",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['base','account_budget','purchase','account_payment','account','account_accountant','report_xlsx'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/budget_transfer_view.xml',
        'views/views.xml',
        'data/data.xml',
        'reports/reports.xml',

    ],
}
