# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import Warning


# Ahmed Salama Code Start ---->


class HrTransfer(models.Model):
	_name = 'hr.transfer'
	_description = "HR Employee Transfer"
	_inherit = ['mail.thread', 'image.mixin']
	
	name = fields.Char("Decision No.",
					   readonly=True, states={'draft': [('readonly', False)]})
	employee_id = fields.Many2one('hr.employee', "Employee", required=True,
								  readonly=True, states={'draft': [('readonly', False)]})
	date = fields.Date("Date", default=fields.Date.today(),
					   readonly=True, states={'draft': [('readonly', False)]})
	state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done')
		                         , ('cancel', 'Cancelled')], default='draft', string="Stage",
	                         track_visibility='onchange')
	change_dep = fields.Boolean("Department Transfer?",
								readonly=True, states={'draft': [('readonly', False)]})
	department_id = fields.Many2one(related='employee_id.department_id', string="Department",
	                                track_visibility='onchange')
	old_department_id = fields.Many2one('hr.department', "Old Department",)
	new_department_id = fields.Many2one('hr.department', "New Department",
										readonly=True, states={'draft': [('readonly', False)]})
	change_loc = fields.Boolean("Location Transfer?",
								readonly=True, states={'draft': [('readonly', False)]})
	location_id = fields.Many2one(related='employee_id.work_location_id', string="Work Location",
	                              track_visibility='onchange')
	old_location_id = fields.Many2one('hr.location', "Old Work Location")
	new_location_id = fields.Many2one('hr.location', "New Work Location",
									  readonly=True, states={'draft': [('readonly', False)]})
	change_job = fields.Boolean("Job Transfer?",
								readonly=True, states={'draft': [('readonly', False)]})
	job_id = fields.Many2one(related='employee_id.job_id', string="Job Position",
	                         track_visibility='onchange')
	old_job_id = fields.Many2one('hr.job', "Old Job Position")
	new_job_id = fields.Many2one('hr.job', "New Job Position",
								 readonly=True, states={'draft': [('readonly', False)]})
	
	def action_confirm(self):
		self.write({'state': 'confirm'})
		messages = ''
		dict_changes = {}
		if self.change_dep and self.new_department_id and self.department_id != self.new_department_id:
			messages += "- Employee [%s] Department [%s] updated to [%s] <br/>" % \
			            (self.employee_id.name, self.department_id.name, self.new_department_id.name)
			self.old_department_id = self.department_id and self.department_id.id or False
			dict_changes['department_id'] = self.new_department_id.id
		if self.change_job and self.new_job_id and self.job_id != self.new_job_id:
			messages += "- Employee [%s] Job [%s] updated to [%s] <br/>" % \
			            (self.employee_id.name, self.job_id.name, self.new_job_id.name)
			self.old_job_id = self.job_id and self.job_id.id or False
			dict_changes['job_id'] = self.new_job_id.id
		if self.change_loc and self.new_location_id and self.location_id != self.new_location_id:
			messages += "- Employee [%s] Work Location [%s] updated to [%s] <br/>" % \
			            (self.employee_id.name, self.location_id.name, self.new_location_id.name)
			self.old_location_id = self.location_id and self.location_id.id or False
			dict_changes['work_location_id'] = self.new_location_id.id
		if dict_changes:
			self.employee_id.write(dict_changes)
		if len(messages):
			self.message_post(body=messages)
	
	def action_cancel(self):
		self.write({'state': 'cancel'})
	
	def action_reset(self):
		self.write({'state': 'draft'})
	
	def action_print_report(self):
		return self.env.ref('egymentors_hr.hr_employee_transfer_report').report_action(self)
		
	def unlink(self):
		for rec in self:
			if rec.state == 'confirm':
				raise Warning(_("You can't delete confirmed records!!!"))
		return super(HrTransfer, self).unlink()
	

# Ahmed Salama Code End.
