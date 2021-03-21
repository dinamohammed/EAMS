# -*- coding: utf-8 -*-
{
    'name': "custome_payslip",

    'summary': """
       This module is custome to get the name of payslip and add to field Referance in account.move
       """,

    'description': """
     This module is custome to get the name of payslip and add to field Referance in account.move
""",

    'author': "Muhammed ashraf ",
    'website': "https://www.egymentors.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_contract','hr_holidays','hr_work_entry','account','hr_payroll', 'account_accountant','mail','web_dashboard'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
