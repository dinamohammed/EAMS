# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning

_STATES = [('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')]
# Ahmed Salama Code Start ---->


class HrTransportationAllowance(models.Model):
	_name = 'hr.trans.allowance'
	_description = "Hr Transportation Allowance"
	_inherit = ['mail.thread', 'image.mixin']

	name = fields.Char("Transportation Allowance",
					   readonly=True, states={'draft': [('readonly', False)]})
	date = fields.Date("Date", default=fields.Date.today(),
					   readonly=True, states={'draft': [('readonly', False)]})
	period_month = fields.Char("Period Month",
							   default=lambda x: fields.Date.today().strftime("%B"),
							   readonly=True, states={'draft': [('readonly', False)]})
	work_location_id = fields.Many2one('hr.location', "Work Location",
									   readonly=True, states={'draft': [('readonly', False)]})

	state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')
	line_ids = fields.One2many('hr.trans.allowance.line', 'trans_id', "Lines", copy=True,
							   readonly=True, states={'draft': [('readonly', False)]})
	state_id = fields.Many2one('res.country.state', "State",
							   readonly=True, states={'draft': [('readonly', False)]},
							   domain=['|', ('country_id.name', '=', "Egypt"), ('country_id.name', '=', "مصر")])

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
		return self.env.ref('egymentors_hr.hr_trans_allowance_report').report_action(self)

	@api.onchange('line_ids')
	@api.depends('line_ids.int_amount', 'line_ids.ext_amount')
	def _get_total_trans_allowance(self):
		for rec in self:
			rec.total_trans_allowance = sum(l.int_amount + l.ext_amount for l in rec.line_ids)
			rec.total_trans_internal = sum(l.int_amount for l in rec.line_ids)
			rec.total_trans_external = sum(l.ext_amount for l in rec.line_ids)

	total_trans_allowance = fields.Float("Total Trans. Allowance", compute=_get_total_trans_allowance)
	total_trans_internal = fields.Float("Internal", compute=_get_total_trans_allowance)
	total_trans_external = fields.Float("External", compute=_get_total_trans_allowance)

	def unlink(self):
		for rec in self:
			if rec.state == 'confirm':
				raise Warning(_("You can't delete confirmed records!!!"))
		return super(HrTransportationAllowance, self).unlink()

	@api.onchange('work_location_id')
	def generate_employee_ids(self):
		emp_obj = self.env['hr.employee']
		for rec in self:
			if rec.work_location_id:
				emps_list = rec.line_ids.mapped('employee_id.id')
				emp_ids = emp_obj.search([('work_location_id', '=', rec.work_location_id.id)])
				for emp_id in emp_ids:
					if emp_id.id not in emps_list:
						rec.line_ids.create({
							'trans_id': rec.id,
							'employee_id': emp_id.id,
						})

	int_days_num = fields.Integer("Internal Days Num.", default=0)

	@api.onchange('int_days_num')
	def _change_all_lines(self):
		self.ensure_one()
		for line in self.line_ids:
			line.int_days_num = self.int_days_num


class HrTransportationAllowanceLine(models.Model):
	_name = 'hr.trans.allowance.line'
	_description = "Hr Transportation Allowance Line"
	_rec_name = 'employee_id'

	trans_id = fields.Many2one('hr.trans.allowance', "Transportation")
	payslip_id = fields.Many2one('hr.payslip', "Payslip")
	date = fields.Date(related='trans_id.date')
	state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')
	work_location_id = fields.Many2one(related='trans_id.work_location_id')
	employee_id = fields.Many2one('hr.employee', "Employee", required=True)

	int_days_num = fields.Integer("Internal Days Num.", default=0)
	ext_days_num = fields.Integer("External Days Num", default=0)
	int_amount = fields.Float("Internal Amount", compute='_compute_trans')
	ext_amount = fields.Float("External Amount", default=1.0)
	notes = fields.Text("Notes")

	@api.onchange('int_days_num', 'work_location_id', 'employee_id')
	@api.depends('employee_id.location_type', 'trans_id.state_id')
	def _compute_trans(self):
		"""
		If type == external (no.days × state. External Amount).
		If type ==  internal (no.days* value [
										- If (employee_id.location_type==dynamic)
												Then value = value added in employee view
										- Else if (employee_id.location_type==static)
												Then value = value added in employee view
										- Else if (employee_id.location_type==management)
												Then Do Nothing ]
		:return: amount
		"""
		configs = self.env['ir.config_parameter'].sudo()
		for line in self:
			ext_amount = int_amount = 0.0
			if line.trans_id.state_id:
				ext_amount = 1 * line.trans_id.state_id.ext_amount
			if line.int_days_num:
				if line.employee_id.location_type == 'dynamic':
					internal_dynamic = float(configs.get_param('internal_dynamic', 0.0))
					int_amount = line.int_days_num * internal_dynamic
				elif line.employee_id.location_type == 'static':
					internal_static = float(configs.get_param('internal_static', 0.0))
					int_amount = line.int_days_num * internal_static
			line.int_amount = int_amount
			line.ext_amount = ext_amount

# Ahmed Salama Code End.

