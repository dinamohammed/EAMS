# -*- coding: utf-8 -*-
{
    'name': "egymaritimesafty",

    'summary': """
        
    """,

    'description': """
        This application manages to identify the need of Organization and Administration Department of employees in each 
        department, so the work is being done fastly, and to create job titles and descriptions for every job, and 
        creating organizational chart, and its approval from the department and present it to Central Agency for 
        Organization and Administration""",

    'author': "Mentors",
    'website': "http://www.mentors.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '14.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/hr_department_views.xml',
        'views/hr_job_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
