# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta

YEAR = 2000  # replace 2000 with your a start year
YEAR_LIST = []
while YEAR != 2030:  # replace 2030 with your end year
    YEAR_LIST.append((str(YEAR), str(YEAR)))
    YEAR += 1


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    level_date = fields.Date(string="Current Level Date")
    grade_id = fields.Many2one(comodel_name='hr.employee.grade', string="Grade")
    percentage = fields.Float(related='grade_id.percentage')
    previous_wage = fields.Float(string="Previous Salary")
    deductions_ids = fields.One2many(comodel_name='hr.employee.deduction', inverse_name='employee_id',
                                     string="Deductions")
    grade_ids = fields.One2many(comodel_name='hr.employee.grade.line', inverse_name='employee_id', string="Grads")
    Syndicate = fields.Selection(selection=[('member', 'Member'), ('not_member', 'Not Member')],
                                 string='Syndicate')
    End_service_subscription = fields.Selection(selection=[('member', 'Member'), ('not_member', 'Not Member')],
                                                string='End of Service Subscription')
    special_needs = fields.Boolean(string="Special Needs")
    accommodation = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string="Accommodation")
    accommodation_type = fields.Selection(selection=[('single', 'Single'), ('group', 'Group')],
                                          string='Accommodation Type')
    transportation = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string="Transportation")
    transportation_type = fields.Selection(selection=[('bus', 'Bus'), ('car', 'Car'), ('microbus', 'Microbus')],
                                           string='Transportation Type')
    seniority_date = fields.Date(string="Seniority Date")
    seniority_years = fields.Integer(string="Years of Seniority", compute='compute_seniority')

    @api.depends('seniority_date')
    def compute_seniority(self):
        self.seniority_years = 0
        for emp in self:
            if emp.seniority_date:
                date_format = '%Y-%m-%d'
                joining_date = str(emp.seniority_date)
                current_date = (datetime.today()).strftime(date_format)
                d1 = datetime.strptime(joining_date, date_format).date()
                d2 = datetime.strptime(current_date, date_format).date()
                emp.seniority_years = relativedelta(d2, d1).years


class HrEmployeeDeduction(models.Model):
    _name = 'hr.employee.deduction'

    employee_id = fields.Many2one('hr.employee', "Employee")
    name = fields.Char("Deduction Number")
    date = fields.Date("Date", default=fields.Date.today().replace(month=1, day=1))
    notes = fields.Text("Notes")
    year = fields.Selection(YEAR_LIST, string="Year", default=str(fields.Date.today().year))

    # as a default value it would be current year

    @api.onchange('year')
    def get_date(self):
        for deduction in self:
            if deduction.year:
                deduction.date = fields.Date.today().replace(year=int(deduction.year), month=1, day=1)

    @api.model
    def create(self, vals):
        vals = self._generate_date(vals)
        return super(HrEmployeeDeduction, self).create(vals)

    def write(self, vals):
        vals = self._generate_date(vals)
        return super(HrEmployeeDeduction, self).write(vals)

    def _generate_date(self, vals):
        if vals.get('year'):
            year_start = fields.Date.today().replace(year=int(vals.get('year')), month=1, day=1)
            vals['date'] = year_start
        return vals


class HrEmployeeGradeLine(models.Model):
    _name = 'hr.employee.grade.line'

    employee_id = fields.Many2one('hr.employee', "Employee")
    grade_id = fields.Many2one('hr.employee.grade', "Grade")
    name = fields.Char("Deduction Number")
    date = fields.Date("Date", default=fields.Date.today().replace(month=1, day=1))
    percentage = fields.Float(related='grade_id.percentage')
    year = fields.Selection(YEAR_LIST, string="Year", default=str(fields.Date.today().year))

    # as a default value it would be current year

    @api.onchange('year')
    def get_date(self):
        for line in self:
            if line.year:
                line.date = fields.Date.today().replace(year=int(line.year), month=1, day=1)

    @api.model
    def create(self, vals):
        vals = self._generate_date(vals)
        return super(HrEmployeeGradeLine, self).create(vals)

    def write(self, vals):
        vals = self._generate_date(vals)
        return super(HrEmployeeGradeLine, self).write(vals)

    def _generate_date(self, vals):
        if vals.get('year'):
            year_start = fields.Date.today().replace(year=int(vals.get('year')), month=1, day=1)
            vals['date'] = year_start
        return vals


class HrEmployeeGrade(models.Model):
    _name = 'hr.employee.grade'

    name = fields.Char("Grade")
    percentage = fields.Float("Percentage")
