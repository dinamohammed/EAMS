# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import Warning

_STATES = [('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')]
# Ahmed Salama Code Start ---->


class HrBonusPenalty(models.Model):
	_name = 'hr.bonus.penalty'
	_description = "Hr Bonus/Penalty"
	_inherit = ['mail.thread', 'image.mixin']
	
	name = fields.Char("Bonus", translate=True)
	extra_type = fields.Selection([('bonus', 'Bonus'),
	                               ('penalty', 'Penalty')], "Type",
								  readonly=True, states={'draft': [('readonly', False)]})
	bonus_type = fields.Selection([('rewards', 'Rewards')],
	                              "Bonus Type", readonly=True, states={'draft': [('readonly', False)]} , default = 'rewards')
    #('allowance', 'Allowance'),
	date = fields.Date("Date", default=fields.Date.today(),
					   readonly=True, states={'draft': [('readonly', False)]})
	fixed_amount = fields.Boolean("Fixed Amount",
								  readonly=True, states={'draft': [('readonly', False)]})
	date_to = fields.Date("To Date",
						  readonly=True, states={'draft': [('readonly', False)]})
	period_month = fields.Char("Period Month",
							   default=lambda x: fields.Date.today().strftime("%B"),
							   readonly=True, states={'draft': [('readonly', False)]})
	work_location_id = fields.Many2one('hr.location', "Work Location",
									   readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')
	line_ids = fields.One2many('hr.bonus.penalty.line', 'bonus_penalty_id', "Lines",
							   readonly=True, states={'draft': [('readonly', False)]})
	
	def _change_state(self, state):
		self.write({'state': state})
		for line in self.line_ids:
			line.write({'state': state})
	
	def action_confirm(self):
		for action in self:
			action._change_state('confirm')
	
	def action_cancel(self):
		for action in self:
			action._change_state('cancel')
	
	def action_reset(self):
		for action in self:
			action._change_state('draft')
	
	def action_print_report(self):
		if self[0].extra_type == 'bonus':
			return self.env.ref('egymentors_hr.hr_bonus_report').report_action(self)
		elif self[0].extra_type == 'penalty':
			return self.env.ref('egymentors_hr.hr_penalty_report').report_action(self)
		else:
			raise Warning(_("Something Went Wrong!!!"))
	
	def unlink(self):
		for rec in self:
			if rec.state == 'confirm':
				raise Warning(_("You can't delete confirmed records!!!"))
		return super(HrBonusPenalty, self).unlink()
	
	@api.onchange('line_ids')
	@api.depends('line_ids.days_num')
	def _get_total_bonus_penalty(self):
		# Bonus
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
		# Penalty
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
			rec.total_bonuses = sum(l.amount for l in rec.line_ids)
			rec.total_penalties = sum(l.days_num for l in rec.line_ids)
			# Penalty
			rec.total_penalties_other = sum(l.days_num for l in
											  rec.line_ids.filtered(lambda x: x.type_id == penalty_other))
			rec.total_penalties_penalty = sum(l.days_num for l in
											  rec.line_ids.filtered(lambda x: x.type_id == penalty_penalty))
			rec.total_penalties_absence = sum(l.days_num for l in
			                                  rec.line_ids.filtered(lambda x: x.type_id == penalty_absence))
			rec.total_penalties_sick = sum(l.days_num for l in
			                               rec.line_ids.filtered(lambda x: x.type_id == penalty_sick))
			rec.total_penalty_unpaid = sum(l.days_num for l in
			                               rec.line_ids.filtered(lambda x: x.type_id == penalty_unpaid))
# 			rec.total_penalty_spare_part = sum(l.days_num for l in
# 			                                   rec.line_ids.filtered(lambda x: x.type_id == penalty_spare_part))
# 			rec.total_penalty_expenditure = sum(l.days_num for l in
# 			                                    rec.line_ids.filtered(lambda x: x.type_id == penalty_expenditure))
# 			rec.total_penalty_impairment = sum(l.days_num for l in
# 			                                   rec.line_ids.filtered(lambda x: x.type_id == penalty_impairment))
			rec.total_penalty_fixed = sum(l.days_num for l in
			                              rec.line_ids.filtered(lambda x: x.type_id == penalty_fixed))
			# Bonus
			# Allowance
# 			rec.total_bonus_production = sum(l.amount for l in
# 			                                 rec.line_ids.filtered(lambda x: x.type_id == bonus_production))
# 			rec.total_bonus_leadership = sum(l.amount for l in
# 			                                 rec.line_ids.filtered(lambda x: x.type_id == bonus_leadership))
# 			rec.total_bonus_workshop = sum(l.amount for l in
# 			                               rec.line_ids.filtered(lambda x: x.type_id == bonus_workshop))
# 			rec.total_bonus_direction = sum(l.amount for l in
# 			                                rec.line_ids.filtered(lambda x: x.type_id == bonus_board_of_direction))
# 			rec.total_bonuses_allowance = sum(l.amount for l in
# 			                                  rec.line_ids.filtered(lambda x: x.type_id.bonus_type == 'allowance'))
			# Rewards
# 			rec.total_bonus_efforts = sum(l.amount for l in
# 			                              rec.line_ids.filtered(lambda x: x.type_id == bonus_efforts))
			rec.total_bonus_rewards = sum(l.amount for l in
			                              rec.line_ids.filtered(lambda x: x.type_id == bonus_rewards))
# 			rec.total_bonus_transportation = sum(l.amount for l in
# 			                                     rec.line_ids.filtered(lambda x: x.type_id == bonus_transportation))
# 			rec.total_bonus_travel = sum(l.amount for l in
# 			                             rec.line_ids.filtered(lambda x: x.type_id == bonus_travel))
# 			rec.total_bonus_additional = sum(l.amount for l in
# 			                                 rec.line_ids.filtered(lambda x: x.type_id == bonus_additional))
# 			rec.total_bonus_feeding = sum(l.amount for l in
# 			                              rec.line_ids.filtered(lambda x: x.type_id == bonus_feeding))
			rec.total_bonuses_rewards = sum(l.amount for l in
			                                rec.line_ids.filtered(lambda x: x.type_id.bonus_type == 'rewards'))
	
	@api.onchange('work_location_id', 'extra_type', 'bonus_type')
	def generate_employee_ids(self):
		emp_obj = self.env['hr.employee']
		type_obj = self.env['hr.bonus.penalty.type']
		for rec in self:
			if rec.extra_type == 'bonus' and rec.work_location_id:
				domain = [('extra_type', '=', 'bonus')]
				if rec.bonus_type:
					domain.append(('bonus_type', '=', rec.bonus_type))
				type_id = type_obj.search(domain, limit=1)
				emps_list = rec.line_ids.mapped('employee_id.id')
				emp_ids = emp_obj.search([('work_location_id', '=', rec.work_location_id.id)])
				for emp_id in emp_ids:
					if emp_id.id not in emps_list:
						rec.line_ids.create({
							'bonus_penalty_id': rec.id,
							'employee_id': emp_id.id,
							'type_id': type_id and type_id.id or False,
						})
	
	total_bonuses = fields.Float("Total Bonuses", compute=_get_total_bonus_penalty)
# 	total_bonuses_allowance = fields.Float("Total Bonuses(Allowance)", compute=_get_total_bonus_penalty)
# 	total_bonus_production = fields.Float("Production", compute=_get_total_bonus_penalty)
# 	total_bonus_leadership = fields.Float("Leadership", compute=_get_total_bonus_penalty)
# 	total_bonus_workshop = fields.Float("Workshop", compute=_get_total_bonus_penalty)
# 	total_bonus_direction = fields.Float("Board of Direction", compute=_get_total_bonus_penalty)
	
	total_bonuses_rewards = fields.Float("Total Bonuses(Rewards)", compute=_get_total_bonus_penalty)
# 	total_bonus_efforts = fields.Float("Efforts", compute=_get_total_bonus_penalty)
	total_bonus_rewards = fields.Float("Rewords", compute=_get_total_bonus_penalty)
# 	total_bonus_transportation = fields.Float("Transportation", compute=_get_total_bonus_penalty)
# 	total_bonus_travel = fields.Float("Travel", compute=_get_total_bonus_penalty)
# 	total_bonus_additional = fields.Float("Additional", compute=_get_total_bonus_penalty)
# 	total_bonus_feeding = fields.Float("Additional", compute=_get_total_bonus_penalty)
	
	total_penalties = fields.Float("Total Penalties", compute=_get_total_bonus_penalty)
	total_penalties_sick = fields.Float("Absence2", compute=_get_total_bonus_penalty)
	total_penalties_other = fields.Float("Other", compute=_get_total_bonus_penalty)
	total_penalties_penalty = fields.Float("Late-Day", compute=_get_total_bonus_penalty)
	total_penalties_absence = fields.Float("Absence", compute=_get_total_bonus_penalty)
	total_penalty_unpaid = fields.Float("Late-Hours", compute=_get_total_bonus_penalty)
# 	total_penalty_spare_part = fields.Float("Spare Part", compute=_get_total_bonus_penalty)
# 	total_penalty_expenditure = fields.Float("Expenditure", compute=_get_total_bonus_penalty)
# 	total_penalty_impairment = fields.Float("Impairment", compute=_get_total_bonus_penalty)
	total_penalty_fixed = fields.Float("Fixed Amount", compute=_get_total_bonus_penalty)


class HrBonusPenaltyLine(models.Model):
	_name = 'hr.bonus.penalty.line'
	_description = "Hr Bonus/Penalty Line"
	_rec_name = 'employee_id'
	
	bonus_penalty_id = fields.Many2one('hr.bonus.penalty', "Bonus/Penalty")
	payslip_id = fields.Many2one('hr.payslip', "Payslip")
	date = fields.Date(related='bonus_penalty_id.date')
	date_to = fields.Date(related='bonus_penalty_id.date_to')
	state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')
	extra_type = fields.Selection(related='bonus_penalty_id.extra_type')
	
	@api.onchange('bonus_penalty_id', 'extra_type')
	@api.depends('bonus_penalty_id.work_location_id')
	def _get_emp_domain(self):
		for line in self:
			domain = []
			if line.extra_type == 'bonus' and line.bonus_penalty_id.work_location_id:
				domain = [('work_location_id', '=', line.bonus_penalty_id.work_location_id.id)]
			return {'domain': {'employee_id': domain}}
	
	employee_id = fields.Many2one('hr.employee', "Employee", required=True, domain=_get_emp_domain)
	type_id = fields.Many2one('hr.bonus.penalty.type', "Type", required=True)
	pre_amount = fields.Float("Amount")
	discount_list = fields.Float("Discount list")
	stop_incentive = fields.Float("Stop incentive")
	amount = fields.Float("Net Amount")

	days_num = fields.Float("Number of Days", default=1)
	notes = fields.Text("Notes")

	def write(self, vals_list):
		for line in self:
			if vals_list.get('pre_amount') or vals_list.get('discount_list')\
				or vals_list.get('stop_incentive') and line.bonus_penalty_id.bonus_type == 'allowance':
				pre_amount = vals_list.get('pre_amount') or line.pre_amount
				discount_list = vals_list.get('discount_list') or line.discount_list
				stop_incentive = vals_list.get('stop_incentive') or line.stop_incentive
				
				vals_list['amount'] = pre_amount - discount_list - stop_incentive
			return super(HrBonusPenaltyLine, self).write(vals_list)



class HrBonusPenaltyType(models.Model):
	_name = 'hr.bonus.penalty.type'
	_description = "Hr Bonus Type"
	
	name = fields.Char("Bonus Type", translate=True)
	extra_type = fields.Selection([('bonus', 'Bonus'),
	                               ('penalty', 'Penalty')], "Type")
	bonus_type = fields.Selection([('rewards', 'Rewards')],
	                              "Bonus Type",default = 'rewards')
    #('allowance', 'Allowance'),
	fixed_amount = fields.Boolean("Fixed Amount",
	                              help="If selected it will add start and end month ")
# Ahmed Salama Code End.
