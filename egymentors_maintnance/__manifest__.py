# -*- coding: utf-8 -*-

{
    'name': "EgyMentors Maintenance",

    'summary': """
        Maintenance Enhancement""",

    'description': """
        Adding some features to Maintenance module, which is:
            Project group of screens:
            - Adding Project screen in the Configuration menu
            - Adding Project Type screen in the Configuration menu
            - Adding Project Location screen in the Configuration menu
            - Adding Project Equipment screen in the Configuration menu
            - Adding Equipment Parts screen  in the Configuration menu
            Task group of screens:
            - Adding Task screen
            - Adding Task Category screen
            - Customising Maintenance Request screen by adding some features
            - Adding Task Lines screen in the main menu
    """,

    'author': "EgyMentors",
    'website': "https://www.egymentors.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '14.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'maintenance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_views_inherit.xml',
        'views/maintenance_project_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
