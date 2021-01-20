# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrPayslipInherit(models.Model):
	_inherit = 'hr.payslip'
	
	loan_line_ids = fields.One2many('hr.loan.line', 'payslip_id', "Loan Lines")
	total_loans = fields.Monetary(compute='_compute_loans')
	
	def compute_sheet(self):
		super(HrPayslipInherit, self).compute_sheet()
		loan_obj = self.env['hr.loan.line']
		for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
			loan_lines = loan_obj.search([('employee_id', '=', payslip.employee_id.id),
			                              ('date', '>=', payslip.date_from),
			                              ('date', '<=', payslip.date_to)])
			loan_lines.write({'payslip_id': payslip.id})
		return True
	
	def _compute_loans(self):
		for payslip in self:
			payslip.total_loans = sum(l.amount for l in payslip.loan_line_ids)

# Ahmed Salama Code End.
