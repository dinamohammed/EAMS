# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning


# Ahmed Salama Code Start ---->


class HrPayRaise(models.Model):
	_name = 'hr.pay.raise'
	_description = "HR Pay Raise"
	_inherit = ['mail.thread', 'image.mixin']
	
	date = fields.Date("Date", default=fields.Date.today(),
					   readonly=True, states={'draft': [('readonly', False)]})
	name = fields.Char("Pay Raise",
					   readonly=True, states={'draft': [('readonly', False)]})
	contract_type_id = fields.Many2one('hr.contract.type', "Contract Type",
									   readonly=True, states={'draft': [('readonly', False)]})
	percentage = fields.Float("Raise Percentage", readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done')
		                         , ('cancel', 'Cancelled')], default='draft', string="Stage",
	                         track_visibility='onchange', copy=False)
	line_ids = fields.One2many('hr.pay.raise.line', 'raise_id', "Pay Raises",
							   readonly=True, states={'draft': [('readonly', False)]})
	
	def action_confirm(self):
		messages = ''
		for line in self.line_ids:
			new_salary = line.contract_id.wage + line.raise_amount
			if new_salary != line.contract_id.wage:
				messages += "- Employee [%s] Basic Salary [%s] updated to [%s] <br/>" % \
				            (line.employee_id.name, line.contract_id.wage, new_salary)
				line.employee_id.write({'previous_wage': line.contract_id.wage})
				line.contract_id.write({'wage': new_salary})
		if len(messages):
			self.message_post(body=messages)
		self.write({'state': 'confirm'})
	
	def action_cancel(self):
		self.write({'state': 'cancel'})
	
	def action_reset(self):
		self.write({'state': 'draft'})
	
	def action_print_report(self):
		return self.env.ref('egymentors_hr.hr_pay_raise_report').report_action(self)
	
	def unlink(self):
		for rec in self:
			if rec.state == 'confirm':
				raise Warning(_("You can't delete confirmed records!!!"))
		return super(HrPayRaise, self).unlink()


class HrPayRaiseLine(models.Model):
	_name = 'hr.pay.raise.line'
	_rec_name = 'raise_id'
	
	raise_id = fields.Many2one('hr.pay.raise', "Pay Raise")
	state = fields.Selection(related='raise_id.state')
	percentage = fields.Float(related='raise_id.percentage')
	currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
	contract_id = fields.Many2one('hr.contract', "Contract")
	employee_id = fields.Many2one(related='contract_id.employee_id')
	basic_salary = fields.Monetary(related='contract_id.wage', string="Basic Salary")
	raise_amount = fields.Monetary("Raise Amount", compute='_compute_line_raise')
	old_salary = fields.Monetary("Old Salary", track_visibility='onchange', compute='_compute_line_raise')
	new_salary = fields.Monetary("New Salary", track_visibility='onchange', compute='_compute_line_raise')
	
	@api.onchange('contract_id', 'basic_salary', 'percentage')
	def _compute_line_raise(self):
		"""
		Its equation= ‘Basic Salary’*(1+ ‘Raise Percentage’)
		"""
		grade_obj = self.env['hr.employee.grade.line']
		configs = self.env['ir.config_parameter'].sudo()
		min_raise = float(configs.get_param('min_raise', 0.0))
		max_raise = float(configs.get_param('max_raise', 0.0))
		for line in self:
			if line.contract_id and line.basic_salary and line.raise_id.percentage:
				if line.state == 'draft':
					raise_amount = line.contract_id.wage * (line.raise_id.percentage / 100)
				elif line.state != 'draft':
					raise_amount = line.employee_id.previous_wage * (line.raise_id.percentage / 100)
				grade_id = grade_obj.search([('employee_id', '=', line.employee_id.id),
				                             ('year', '=', str(fields.Date.today().year))])
				if grade_id:
					raise_amount = raise_amount * (grade_id.percentage / 100)
				if min_raise > raise_amount:
					raise_amount = min_raise
				elif max_raise < raise_amount:
					raise_amount = max_raise
				line.raise_amount = raise_amount
				if line.state == 'draft':
					line.old_salary = line.basic_salary
					line.new_salary = line.basic_salary + raise_amount
				elif line.state == 'confirm':
					line.old_salary = line.employee_id.previous_wage
					line.new_salary = line.basic_salary


# Ahmed Salama Code End.
