# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import Warning


# Ahmed Salama Code Start ---->


class HrPromotion(models.Model):
	_name = 'hr.promotion'
	_description = "HR Employee Transfer"
	_inherit = ['mail.thread', 'image.mixin']
	
	date = fields.Date("Date", default=fields.Date.today(),
					   readonly=True, states={'draft': [('readonly', False)]})
	name = fields.Char("Decision No.",
					   readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done')
		                         , ('cancel', 'Cancelled')], default='draft', string="Stage",
	                         track_visibility='onchange')
	line_ids = fields.One2many('hr.promotion.line', 'action_id', "Lines",
							   track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
	
	def action_confirm(self):
		messages = ''
		for line in self.line_ids:
			if line.new_level_id and line.level_id != line.new_level_id:
				messages += "- Employee [%s] Level [%s] updated to [%s] <br/>" % \
				            (line.employee_id.name, line.level_id.name, line.new_level_id.name)
				line.old_level_id = line.level_id and line.level_id.id or False
				line.employee_id.write({'level_id': line.new_level_id.id, 'level_date': self.date})
		if len(messages):
			self.message_post(body=messages)
		self.write({'state': 'confirm'})

	
	def action_cancel(self):
		self.write({'state': 'cancel'})
	
	def action_reset(self):
		self.write({'state': 'draft'})
	
	def action_print_report(self):
		return self.env.ref('egymentors_hr.hr_employee_promotion_report').report_action(self)
		
	def unlink(self):
		for rec in self:
			if rec.state == 'confirm':
				raise Warning(_("You can't delete confirmed records!!!"))
		return super(HrPromotion, self).unlink()


class HrEmployeeActionLine(models.Model):
	_name = 'hr.promotion.line'
	_rec_name = 'action_id'
	
	action_id = fields.Many2one('hr.promotion', "Action")
	state = fields.Selection(related='action_id.state')
	employee_id = fields.Many2one('hr.employee', "Employee", required=True)
	
	@api.onchange('employee_id')
	@api.depends('employee_id.level_date')
	def _get_level_date(self):
		for line in self:
			if line.employee_id:
				line.level_date = line.employee_id.level_date
				
	@api.model
	def create(self, vals):
		if vals.get('employee_id'):
			emp_id = self.env['hr.employee'].browse(vals.get('employee_id'))
			if emp_id and emp_id.level_date:
				vals['level_date'] = emp_id.level_date
		return super(HrEmployeeActionLine, self).create(vals)
	
	def write(self, vals):
		if vals.get('employee_id'):
			emp_id = self.env['hr.employee'].browse(vals.get('employee_id'))
			if emp_id and emp_id.level_date:
				vals['level_date'] = emp_id.level_date
		return super(HrEmployeeActionLine, self).write(vals)
		
	level_date = fields.Date("Current Level Date")
	level_id = fields.Many2one(related='employee_id.level_id', string="Current Level", track_visibility='onchange')
	old_level_id = fields.Many2one('hr.level', "Old Level")
	new_level_id = fields.Many2one('hr.level', "New Level")


# Ahmed Salama Code End.
