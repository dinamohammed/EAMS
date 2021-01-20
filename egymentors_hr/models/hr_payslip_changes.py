# -*- coding: utf-8 -*-
import base64

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from odoo.tools.safe_eval import safe_eval


# Ahmed Salama Code Start ---->


class HrPayslipInherit(models.Model):
	_inherit = 'hr.payslip'
	
	# BONUS PART
	# ####################################################
	def _get_hr_bonuses(self):
		bonus_line_obj = self.env['hr.bonus.penalty.line']
		for payslip in self:
			if payslip.employee_id:
				domain = [('employee_id', '=', payslip.employee_id.id),
				          ('state', '=', 'confirm'), ('extra_type', '=', 'bonus')]
				if payslip.date_from:
					domain.append(('date', '>=', payslip.date_from))
				if payslip.date_to:
					domain.append(('date', '<=', payslip.date_to))
				payslip.write({'hr_bonus_ids': [(6, 0, bonus_line_obj.search(domain).mapped('id'))]})
	
	hr_bonus_ids = fields.One2many('hr.bonus.penalty.line', 'payslip_id', "Bonuses",
	                               domain=[('extra_type', '=', 'bonus')])
	
	@api.onchange('hr_bonus_ids')
	@api.depends('hr_bonus_ids.amount')
	def _get_total_bonus(self):
# 		bonus_production = self.env.ref('egymentors_hr.bonus_production')
# 		bonus_leadership = self.env.ref('egymentors_hr.bonus_leadership')
# 		bonus_board_of_direction = self.env.ref('egymentors_hr.bonus_board_of_direction')
# 		bonus_workshop = self.env.ref('egymentors_hr.bonus_workshop')
# 		bonus_efforts = self.env.ref('egymentors_hr.bonus_efforts')
		bonus_rewards = self.env.ref('egymentors_hr.bonus_rewards')
# 		bonus_transportation = self.env.ref('egymentors_hr.bonus_transportation')
# 		bonus_travel = self.env.ref('egymentors_hr.bonus_travel')
# 		bonus_additional = self.env.ref('egymentors_hr.bonus_additional')
# 		bonus_feeding = self.env.ref('egymentors_hr.bonus_feeding')
		for rec in self:
			rec.total_bonuses = sum(l.amount for l in rec.hr_bonus_ids)
			# Allowance
# 			rec.total_bonus_production = sum(l.amount for l in
# 			                                 rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_production))
# 			rec.total_bonus_leadership = sum(l.amount for l in
# 			                                 rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_leadership))
# 			rec.total_bonus_workshop = sum(l.amount for l in
# 			                               rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_workshop))
# 			rec.total_bonus_direction = sum(l.amount for l in
# 			                                rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_board_of_direction))
# 			rec.total_bonuses_allowance = sum(l.amount for l in
# 			                                  rec.hr_bonus_ids.filtered(lambda x:x.type_id.bonus_type == 'allowance'))
			# Rewards
# 			rec.total_bonus_efforts = sum(l.amount for l in
# 			                              rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_efforts))
			rec.total_bonus_rewards = sum(l.amount for l in
 			                              rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_rewards))
# 			rec.total_bonus_transportation = sum(l.amount for l in
# 			                                     rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_transportation))
# 			rec.total_bonus_travel = sum(l.amount for l in
# 			                             rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_travel))
# 			rec.total_bonus_additional = sum(l.amount for l in
# 			                                 rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_additional))
# 			rec.total_bonus_feeding = sum(l.amount for l in
# 			                              rec.hr_bonus_ids.filtered(lambda x: x.type_id == bonus_feeding))
			rec.total_bonuses_rewards = sum(l.amount for l in
			                                rec.hr_bonus_ids.filtered(lambda x:x.type_id.bonus_type == 'rewards'))
	
	total_bonuses = fields.Float("Total Bonuses", compute=_get_total_bonus)
# 	total_bonuses_allowance = fields.Float("Total Bonuses(Allowance)", compute=_get_total_bonus)
	total_bonuses_rewards = fields.Float("Total Bonuses(Rewards)", compute=_get_total_bonus)
# 	total_bonus_production = fields.Float("Production", compute=_get_total_bonus)
# 	total_bonus_leadership = fields.Float("Leadership", compute=_get_total_bonus)
# 	total_bonus_workshop = fields.Float("Workshop", compute=_get_total_bonus)
# 	total_bonus_direction = fields.Float("Board of Direction", compute=_get_total_bonus)
# 	total_bonus_efforts = fields.Float("Efforts", compute=_get_total_bonus)
	total_bonus_rewards = fields.Float("Rewords", compute=_get_total_bonus)
# 	total_bonus_transportation = fields.Float("Transportation", compute=_get_total_bonus)
# 	total_bonus_travel = fields.Float("Travel", compute=_get_total_bonus)
# 	total_bonus_additional = fields.Float("Additional", compute=_get_total_bonus)
# 	total_bonus_feeding = fields.Float("Additional", compute=_get_total_bonus)
# 	total_bonus_other = fields.Float("Other")
	
	# PENALTY PART
	# ####################################################
	def _get_hr_penalties(self):
		penalty_fixed = self.env.ref('egymentors_hr.penalty_fixed')
		penalty_line_obj = self.env['hr.bonus.penalty.line']
		for payslip in self:
			if payslip.employee_id:
				# Non Fixed Types
				domain = [('employee_id', '=', payslip.employee_id.id),
				          ('state', '=', 'confirm'), ('extra_type', '=', 'penalty')]
				if payslip.date_from:
					domain.append(('date', '>=', payslip.date_from))
				if payslip.date_to:
					domain.append(('date', '<=', payslip.date_to))
				penalty_line_ids = penalty_line_obj.search(domain).mapped('id')
				# Fixed Types
				penalty_fixed_ids = penalty_line_obj.search([('type_id', '=', penalty_fixed.id),
				                                             ('employee_id', '=', payslip.employee_id.id),
				                                             ('state', '=', 'confirm'),
				                                             ('date', '<=', payslip.date_from),
				                                             ('date_to', '>=', payslip.date_from)])
				if penalty_fixed_ids:
					for l in penalty_fixed_ids:
						penalty_line_ids.append(l.id)
				payslip.write({'hr_penalty_ids': [(6, 0, penalty_line_ids)]})
	
	hr_penalty_ids = fields.One2many('hr.bonus.penalty.line', 'payslip_id', "Penalties",
	                                 domain=[('extra_type', '=', 'penalty')])
	
	@api.onchange('hr_penalty_ids')
	@api.depends('hr_penalty_ids.days_num')
	def _get_total_penalty(self):
		penalty_other = self.env.ref('egymentors_hr.penalty_other')
		penalty_penalty = self.env.ref('egymentors_hr.penalty_penalty')
		penalty_absence = self.env.ref('egymentors_hr.penalty_absence')
		penalty_sick = self.env.ref('egymentors_hr.penalty_sick')
		penalty_unpaid = self.env.ref('egymentors_hr.penalty_unpaid')
# 		penalty_spare_part = self.env.ref('egymentors_hr.penalty_spare_part')
# 		penalty_expenditure = self.env.ref('egymentors_hr.penalty_expenditure')
# 		penalty_impairment = self.env.ref('egymentors_hr.penalty_impairment')
		penalty_fixed = self.env.ref('egymentors_hr.penalty_fixed')
		for rec in self:
			rec.total_penalties = sum(l.days_num for l in rec.hr_penalty_ids)
			# Penalty
			rec.total_penalties_other = sum(l.days_num for l in
			                                rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_other))
			rec.total_penalties_penalty = sum(l.days_num for l in
			                                  rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_penalty))
			rec.total_penalties_absence = sum(l.days_num for l in
			                                  rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_absence))
			rec.total_penalties_sick = sum(l.days_num for l in
			                               rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_sick))
			rec.total_penalty_unpaid = sum(l.days_num for l in
			                               rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_unpaid))
# 			rec.total_penalty_spare_part = sum(l.days_num for l in
# 			                                   rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_spare_part))
# 			rec.total_penalty_expenditure = sum(l.days_num for l in
# 			                                    rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_expenditure))
# 			rec.total_penalty_impairment = sum(l.days_num for l in
# 			                                   rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_impairment))
			rec.total_penalty_fixed = sum(l.days_num for l in
			                              rec.hr_penalty_ids.filtered(lambda x: x.type_id == penalty_fixed))
	
	total_penalties = fields.Float("Total Penalties", compute=_get_total_penalty)
	total_penalties_sick = fields.Float("Absence2", compute=_get_total_penalty)
	total_penalties_other = fields.Float("Other", compute=_get_total_penalty)
	total_penalties_penalty = fields.Float("Late-Day", compute=_get_total_penalty)
	total_penalties_absence = fields.Float("Absence", compute=_get_total_penalty)
	total_penalty_unpaid = fields.Float("Late-Hours", compute=_get_total_penalty)
# 	total_penalty_spare_part = fields.Float("Spare Part", compute=_get_total_penalty)
# 	total_penalty_expenditure = fields.Float("Expenditure", compute=_get_total_penalty)
# 	total_penalty_impairment = fields.Float("Impairment", compute=_get_total_penalty)
	total_penalty_fixed = fields.Float("Fixed Amount", compute=_get_total_penalty)
	
	# Transportation Allowance PART
	# ####################################################
	def _get_hr_trans_allowance(self):
		trans_line_obj = self.env['hr.trans.allowance.line']
		for payslip in self:
			if payslip.employee_id:
				domain = [('employee_id', '=', payslip.employee_id.id),
				          ('state', '=', 'confirm')]
				if payslip.date_from:
					domain.append(('date', '>=', payslip.date_from))
				if payslip.date_to:
					domain.append(('date', '<=', payslip.date_to))
				payslip.write({'hr_trans_lines_ids': [(6, 0, trans_line_obj.search(domain).mapped('id'))]})
	
	hr_trans_lines_ids = fields.One2many('hr.trans.allowance.line', 'payslip_id', "Transportation Allowance")
	
	@api.onchange('hr_trans_lines_ids')
	@api.depends('hr_trans_lines_ids.int_amount', 'hr_trans_lines_ids.ext_amount')
	def _get_total_trans_allowance(self):
		for rec in self:
			rec.total_trans_allowance = sum(l.int_amount + l.ext_amount for l in rec.hr_trans_lines_ids)
			rec.total_trans_internal = sum(l.int_amount for l in rec.hr_trans_lines_ids)
			rec.total_trans_external = sum(l.ext_amount for l in rec.hr_trans_lines_ids)
	
	total_trans_allowance = fields.Float("Total Trans. Allowance", compute=_get_total_trans_allowance)
	total_trans_internal = fields.Float("Internal", compute=_get_total_trans_allowance)
	total_trans_external = fields.Float("External", compute=_get_total_trans_allowance)
	
	@api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
	def _onchange_employee(self):
		super(HrPayslipInherit, self)._onchange_employee()
		self._get_hr_bonuses()
		self._get_hr_penalties()
		self._get_hr_trans_allowance()
		self._get_hr_award_profit()
	
	def action_payslip_done(self):
		"""
		Append Function to add extra action action_set_line_confirm
		:return: SUPER
		"""
		lines_dicts = [{'lines': self.hr_bonus_ids, 'inverse_name': 'bonus_penalty_id'},
		               {'lines': self.hr_penalty_ids, 'inverse_name': 'bonus_penalty_id'},
		               {'lines': self.hr_award_profit_ids, 'inverse_name': 'award_profit_id'},
		               {'lines': self.hr_trans_lines_ids, 'inverse_name': 'trans_id'}]
		for lines_dict in lines_dicts:
			self.action_set_line_confirm(lines_dict)
		return super(HrPayslipInherit, self).action_payslip_done()
	
	def action_set_line_confirm(self, lines_dict):
		"""
		Change State of this field lines to done to avoid using it on another payslip
		:param lines_dict: one2many field of those lines
		"""
		for line in lines_dict['lines']:
			line.write({'state': 'done'})
			main_field = getattr(line, lines_dict['inverse_name'])
			if all(state == 'done' for state in main_field.line_ids.mapped('state')):
				main_field.write({'state': 'done'})
	
	def default_action_payslip_done(self):
		if any(slip.state == 'cancel' for slip in self):
			raise ValidationError(_("You can't validate a cancelled payslip."))
		self.write({'state': 'done'})
		self.mapped('payslip_run_id').action_close()
		if self.env.context.get('payslip_generate_pdf'):
			for payslip in self:
				if not payslip.struct_id or not payslip.struct_id.report_id:
					report = self.env.ref('hr_payroll.action_report_payslip', False)
				else:
					report = payslip.struct_id.report_id
				pdf_content, content_type = report.render_qweb_pdf(payslip.id)
				if payslip.struct_id.report_id.print_report_name:
					pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
				else:
					pdf_name = _("Payslip")
				self.env['ir.attachment'].create({
					'name': pdf_name,
					'type': 'binary',
					'datas': base64.encodestring(pdf_content),
					'res_model': payslip._name,
					'res_id': payslip.id
				})
	
	# BONUS PART
	# ####################################################
	def _get_hr_award_profit(self):
		line_obj = self.env['hr.award.profit.line']
		for payslip in self:
			if payslip.employee_id:
				domain = [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'confirm')]
				if payslip.date_from:
					domain.append(('date', '>=', payslip.date_from))
				if payslip.date_to:
					domain.append(('date', '<=', payslip.date_to))
				payslip.write({'hr_award_profit_ids': [(6, 0, line_obj.search(domain).mapped('id'))]})
	
	hr_award_profit_ids = fields.One2many('hr.award.profit.line', 'payslip_id', "Award/Profit")
	
	@api.onchange('hr_award_profit_ids')
	@api.depends('hr_award_profit_ids.amount')
	def _get_total_award_profit(self):
		for rec in self:
			rec.total_award_profit = sum(l.amount for l in rec.hr_award_profit_ids)
			rec.total_award = sum(l.amount for l in
			                      rec.hr_award_profit_ids.filtered(lambda x: x.award_profit_id.extra_type == 'award'))
			rec.total_profit = sum(l.amount for l in
			                       rec.hr_award_profit_ids.filtered(lambda x: x.award_profit_id.extra_type == 'profit'))
	
	total_award_profit = fields.Float("Total Award/Profit", compute=_get_total_award_profit)
	total_award = fields.Float("Award", compute=_get_total_award_profit)
	total_profit = fields.Float("Profit", compute=_get_total_award_profit)
	
	# Collect Report Data
	def get_salary_rules(self):
		salary_rules = []
		for payslip_id in self:
			for line in payslip_id.line_ids:
				if line.total and line.salary_rule_id.appears_on_payslip \
						and line.salary_rule_id.id not in salary_rules:
					salary_rules.append(line.salary_rule_id.id)
		return salary_rules
	
	def assign_parents_and_free_rules(self):
		"""
		Get payslips rules and seprate them according to parent
		:return:
		- dict of parent and it's rules ids
		- list of rules ids which have no parents
		"""
		salary_rules_obj = self.env['hr.salary.rule']
		salary_rules = self.get_salary_rules()
		salary_rule_ids = salary_rules_obj.browse(salary_rules).sorted(lambda l: l.sequence)
		salary_rule_parent = {}
		rules_without_parent = []
		for rule in salary_rule_ids:
			if rule.parent_id:
				if rule.parent_id.id in salary_rule_parent.keys():
					# Parent Exist collect rules
					if rule.id not in salary_rule_parent[rule.parent_id.id]:
						salary_rule_parent[rule.parent_id.id].append(rule.id)
				else:
					# new parent
					salary_rule_parent[rule.parent_id.id] = [rule.id]
			else:
				# fill list of rules without parents
				rules_without_parent.append(rule.id)
		return salary_rule_parent, rules_without_parent
	
	def get_rule_parents_and_free(self, parent=False):
		"""
		This will return object of parents and rules
		:param parent:
		:return:
		"""
		salary_rule_parent_obj = self.env['hr.salary.rule.parent']
		salary_rules_obj = self.env['hr.salary.rule']
		salary_rule_parent, rules_without_parent = self.assign_parents_and_free_rules()
		parents = salary_rule_parent_obj.browse([r for r in salary_rule_parent])
		if parent:
			return parents.mapped('name')
		else:
			return salary_rules_obj.browse(rules_without_parent).mapped('name')
	
	def get_parent_amount(self, salary_rule_parent):
		payslip_line_obj = self.env['hr.payslip.line']
		list_of_totals = []
		for parent in salary_rule_parent:
			total = sum(l.total for l in payslip_line_obj.search([('salary_rule_id', 'in', salary_rule_parent[parent]),
			                                                      ('slip_id', 'in', self.ids)]))
			list_of_totals.append(round(total, 2))
		return list_of_totals
	
	def get_free_rule_amount(self, rules_without_parent):
		payslip_line_obj = self.env['hr.payslip.line']
		list_of_totals = []
		for rule in rules_without_parent:
			total = sum(l.total for l in payslip_line_obj.search([('salary_rule_id', '=', rule),
			                                                      ('slip_id', 'in', self.ids)]))
			list_of_totals.append(round(total, 2))
		return list_of_totals


class HrPayslipRun(models.Model):
	_inherit = 'hr.payslip.run'
	
	all_employees = fields.Boolean('All Employees', default=False)
	
	work_location_id = fields.Many2one('hr.location', "Work Location")
	company_id = fields.Many2one('res.company', string='Company')
	department_id = fields.Many2one('hr.department', "Department")

# Ahmed Salama Code End.
