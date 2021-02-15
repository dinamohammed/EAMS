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
    'name': "EgyMentors Loan",
    'author': 'EgyMentors, Ahmed Salama',
    'category': 'Human Resources',
    'summary': """ New Object for employees loans""",
    'website': 'http://www.egymentors.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '10.0',
    'depends': ['hr', 'hr_payroll'],
    'data': [
        'data/loan_data.xml',
        
        'security/ir.model.access.csv',
        
        'views/hr_loan.xml',
        'views/hr_employee_view_changes.xml',
        'views/hr_payroll_view_changes.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
