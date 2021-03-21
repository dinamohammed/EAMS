# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Check Management (Bank check)',
    'version': '1.0',
    'description': """
        This module is used to enhance Account Cheque module .
        ==============================================
            * Add new state/operation [In Bank] to create this state journals.
            * Add new action to return third check with selected partner.
            * Change accounts that created from Debited action.
    """,
    'category': 'Accounting',
    'summary': 'Accounting, Payment, Check, Received, Issue',
    'author': 'Ahmed Salama<asalama@zadsolutions.com>',
    'website': 'https://zadsolutions.com',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': ['stock', 'account', 'account_check_printing'
                # for bank and cash menu and also for better usability
                #'account_payment_fix',
                ],
    'data': [
        'data/account_payment_method_data.xml',
        
        'wizard/supplier_check_action_wizard.xml',
        'wizard/check_action_view_changes.xml',
        
        'views/account_payment_view.xml',
        'views/account_check_view.xml',
        'views/account_journal_dashboard_view.xml',
        'views/account_journal_view.xml',
        'views/account_checkbook_view.xml',
        # 'views/res_company_view.xml',
        'views/res_config_view_changes.xml',
        'views/account_chart_template_view.xml',
        
        'security/ir.model.access.csv',
        'security/account_check_security.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'images': ['static/description/main.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 49.99,
    'currency': 'EUR',
}
