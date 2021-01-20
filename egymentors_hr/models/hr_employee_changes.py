# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


# Ahmed Salama Code Start ---->
YEAR = 2000  # replace 2000 with your a start year
YEAR_LIST = []
while YEAR != 2030:  # replace 2030 with your end year
    YEAR_LIST.append((str(YEAR), str(YEAR)))
    YEAR += 1


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'
    
    level_date = fields.Date("Current Level Date")
    grade_id = fields.Many2one('hr.employee.grade', "Grade")
    percentage = fields.Float(related='grade_id.percentage')
    previous_wage = fields.Float("Previous Salary")
    deductions_ids = fields.One2many('hr.employee.deduction', 'employee_id', "Deductions")
    grade_ids = fields.One2many('hr.employee.grade.line', 'employee_id', "Grads")
    

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
