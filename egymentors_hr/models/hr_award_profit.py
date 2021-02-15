# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import Warning

_STATES = [('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')]
# Ahmed Salama Code Start ---->


class HrAwardProfit(models.Model):
    _name = 'hr.award.profit'
    _description = "Hr Award/Profit"
    _inherit = ['mail.thread', 'image.mixin']

    name = fields.Char("Award/Profit", translate=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    extra_type = fields.Selection([('award', 'Award'), ('profit', 'Profit')], "Type"
                                  , readonly=True, states={'draft': [('readonly', False)]})

    select_by = fields.Selection([('work_loc', 'Work Location'), ('all', 'All')], "Select By"
                                  , readonly=True, states={'draft': [('readonly', False)]})

    date = fields.Date("Date", default=fields.Date.today(),
                       readonly=True, states={'draft': [('readonly', False)]})

    work_location_id = fields.Many2one('hr.location', "Work Location",
                                       readonly=True, states={'draft': [('readonly', False)]})


    #ertrac_company = fields.Many2one('ertrac.company', "All Employees", readonly=True, states={'draft': [('readonly', False)]})


    company_id = fields.Many2one('res.company', string='Company', states={'draft': [('readonly', False)]})

    state = fields.Selection(_STATES, default='draft', string="Stage",
                             track_visibility='onchange')
    line_ids = fields.One2many('hr.award.profit.line', 'award_profit_id', "Lines",
                               readonly=True, states={'draft': [('readonly', False)]})
    award_value = fields.Float("Award Value", readonly=True, states={'draft': [('readonly', False)]})
    num_months = fields.Float("Number Of Months", readonly=True, states={'draft': [('readonly', False)]})

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
        return self.env.ref('egymentors_hr.hr_award_profit_report').report_action(self)

    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise Warning(_("You can't delete confirmed records!!!"))
        return super(HrAwardProfit, self).unlink()

    @api.onchange('line_ids')
    def _get_total(self):
        for rec in self:
            rec.total_amount = sum(l.amount for l in rec.line_ids)

    total_amount = fields.Float("Total", compute=_get_total)


    @api.onchange('award_value')
    def generate_all_employee_ids(self):
        emp_obj = self.env['hr.employee']
        for rec in self:
            if rec.company_id:
                emps_list = rec.line_ids.mapped('employee_id.id')
                emp_ids = emp_obj.search([('company_id', '=', rec.company_id.id)])
                for emp_id in emp_ids:
                    if emp_id.id not in emps_list:
                        amount = 0.0
                        if rec.extra_type == 'award':
                            amount = rec.award_value
                        if rec.extra_type == 'profit' and emp_id.previous_wage:
                            amount = emp_id.previous_wage * rec.num_months
                        rec.line_ids.create({
                            'award_profit_id': rec.id,
                            'employee_id': emp_id.id,
                            'amount': amount

                        })

    @api.onchange('company_id')
    def generate_all_employee_ids(self):
        emp_obj = self.env['hr.employee']
        for rec in self:
            if rec.company_id:
                emps_list = rec.line_ids.mapped('employee_id.id')
                emp_ids = emp_obj.search([('company_id', '=', rec.company_id.id)])
                for emp_id in emp_ids:
                    if emp_id.id not in emps_list:
                        amount = 0.0
                        if rec.extra_type == 'award':
                            amount = rec.award_value
                        if rec.extra_type == 'profit' and emp_id.previous_wage:
                            amount = emp_id.previous_wage * rec.num_months
                        rec.line_ids.create({
                            'award_profit_id': rec.id,
                            'employee_id': emp_id.id,
                            'amount': amount

                        })

    @api.onchange('award_value')
    def generate_employee_ids(self):
        emp_obj = self.env['hr.employee']
        for rec in self:
            if rec.work_location_id:
                emps_list = rec.line_ids.mapped('employee_id.id')
                emp_ids = emp_obj.search([('work_location_id', '=', rec.work_location_id.id)])
                for emp_id in emp_ids:
                    if emp_id.id not in emps_list:
                        amount = 0.0
                        if rec.extra_type == 'award':
                            amount = rec.award_value
                        if rec.extra_type == 'profit' and emp_id.previous_wage:
                            amount = emp_id.previous_wage * rec.num_months
                        rec.line_ids.create({
                            'award_profit_id': rec.id,
                            'employee_id': emp_id.id,
                            'amount': amount

                        })

    @api.onchange('work_location_id')
    def generate_employee_ids(self):
        emp_obj = self.env['hr.employee']
        for rec in self:
            if rec.work_location_id:
                emps_list = rec.line_ids.mapped('employee_id.id')
                emp_ids = emp_obj.search([('work_location_id', '=', rec.work_location_id.id)])
                for emp_id in emp_ids:
                    if emp_id.id not in emps_list:
                        amount = 0.0
                        if rec.extra_type == 'award':
                            amount = rec.award_value
                        if rec.extra_type == 'profit' and emp_id.previous_wage:
                            amount = emp_id.previous_wage * rec.num_months
                        rec.line_ids.create({
                            'award_profit_id': rec.id,
                            'employee_id': emp_id.id,
                            'amount': amount

                        })

    @api.onchange('award_value')
    def on_change_award_value(self):
        for rec in self:
            for line in rec.line_ids:
                if rec.extra_type == 'award':
                    line.amount = rec.award_value
                    line.write({'amount': rec.award_value})


    def write(self, vals):
        for rec in self:
            amount = 0
            if vals.get('extra_type') or vals.get('award_value') or vals.get('num_months'):
                num_months = vals.get('num_months') or rec.num_months
                award_value = vals.get('award_value') or rec.award_value
                extra_type = vals.get('extra_type') or rec.extra_type
                for line in rec.line_ids:
                    if extra_type == 'award':
                        amount = award_value
                    elif extra_type == 'profit' and line.employee_id.previous_wage:
                        amount = line.employee_id.previous_wage * num_months
                    line.amount = amount
            return super(HrAwardProfit, self).write(vals)


class HrBonusPenaltyLine(models.Model):
    _name = 'hr.award.profit.line'
    _description = "Hr Award/Profit Line"
    _rec_name = 'employee_id'

    award_profit_id = fields.Many2one('hr.award.profit', "Award/Profit")
    payslip_id = fields.Many2one('hr.payslip', "Payslip")
    date = fields.Date(related='award_profit_id.date')
    state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')
    extra_type = fields.Selection(related='award_profit_id.extra_type')

    @api.onchange('award_profit_id', 'extra_type')
    @api.depends('award_profit_id.work_location_id')
    def _get_emp_domain(self):
        for line in self:
            domain = []
            if line.extra_type == 'bonus' and line.award_profit_id.work_location_id:
                domain = [('work_location_id', '=', line.award_profit_id.work_location_id.id)]
            if line.extra_type == 'bonus' and line.award_profit_id.ertrac_company:
                domain = [('ertrac_company', '=', line.award_profit_id.ertrac_company.id)]
            return {'domain': {'employee_id': domain}}

    employee_id = fields.Many2one('hr.employee', "Employee", required=True, domain=_get_emp_domain)
    amount = fields.Float("Amount")
    notes = fields.Text("Notes")

# Ahmed Salama Code End.
