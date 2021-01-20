# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
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
#################################################################################

{
    'name': "EgyMentors Human Resources Enhancement[ercac]",
    'author': 'EgyMentors, Ahmed Salama',
    'category': 'HR',
    'summary': """Human Resources Enhancement""",
    'website': 'http://www.egymentors.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '10.0',
    'depends': ['report_xlsx', 'hr', 'tags__rule', 'hr_payroll_account'],
    'data': [
        'data/hr_bonus_penalty_data.xml',
        'data/hr_grade_date.xml',
        
        'security/ir.model.access.csv',
        
        'views/res_config_view_changes.xml',
        'views/hr_employee_view_changes.xml',
        'views/hr_bonus_view.xml',
        'views/hr_penalty_view.xml',
        'views/hr_promotion_view.xml',
        'views/hr_transfer_view.xml',
        'views/hr_pay_raise_view.xml',
        'views/report_hr_bonus.xml',
        'views/report_hr_penalty.xml',
        'views/hr_payslip_view_inherit.xml',
        'views/res_country_state_view_changes.xml',
        'views/hr_contract_view_changes.xml',
        'views/hr_trans_allowance_view.xml',
        'views/hr_award_profit_view.xml',
        'views/hr_salary_rule_view_changes.xml',

        'reports/reports.xml',
        'views/report_hr_employee_promotion.xml',
        'views/report_hr_employee_transfer.xml',
        'views/report_hr_pay_raise.xml',
        'views/report_hr_trans_allowance.xml',
        'views/report_hr_award_profit.xml',
        'views/report_payslip_salary_rules_pdf.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
