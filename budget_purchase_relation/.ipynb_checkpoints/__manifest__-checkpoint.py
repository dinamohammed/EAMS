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
    'depends': ['base','account_budget','purchase'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
