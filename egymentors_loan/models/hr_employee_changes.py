# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrEmployee(models.Model):
    _inherit = "hr.employee"
    
    def _compute_employee_loans(self):
        """This compute the loan amount and total loans count of an employee.
            """
        self.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', self.id)])
        
    loan_count = fields.Integer(string="Loan Count", compute='_compute_employee_loans')

    def open_employee_loans(self):
        compose_tree = self.env.ref('egymentors_loan.hr_loan_tree_view', False)
        return {
            'name': '%s Loans' % self.name,
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hr.loan',
            'view_id': compose_tree.id,
            'target': 'current',
            'domain': [('employee_id', '=', self.id)],
        }

# Ahmed Salama Code End.
