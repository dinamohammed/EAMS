# -*- coding: utf-8 -*-
{
    'name': "Tags_Rule",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Egymentors",
    'website': "http://www.egymentors.com",
    'category': 'Human Resource',
    'version': '0.2',
    'depends': ['base','hr_payroll', 'hr','hr_holidays'],
    'data': [
        'data/hr_level_data.xml',
        'data/ir_cron_data.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/location.xml',
        'views/level.xml',
        'views/hr_leave_level.xml',
        'views/contractType.xml',
        'views/search.xml',
        'views/res_config_settings_view.xml',
    ],
}
