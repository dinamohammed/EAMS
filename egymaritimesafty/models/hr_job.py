# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class JobPosition(models.Model):
    _inherit = 'hr.job'

    job_title_degree_id = fields.Many2one(comodel_name='hr.job.degree', string="Job Title - Degree", required=True)
    job_functional_id = fields.Many2one(related='job_title_degree_id.job_functional_id')
    job_qualitative_id = fields.Many2one(related='job_title_degree_id.job_qualitative_id')
    job_title_id = fields.Many2one(related='job_title_degree_id.job_title_id')
    job_degree = fields.Char(related='job_title_degree_id.name')
    name = fields.Char(string='Job Position', required=False, index=True, translate=True)
    emp_no = fields.Integer(string="Number of Employees", compute='_compute_job_count')
    financial_degree = fields.Selection(related='job_title_degree_id.financial_degree')
    starting_degree_salary = fields.Float(related='job_title_degree_id.starting_degree_salary')
    duration = fields.Integer(related='job_title_degree_id.duration')
    promotion_percent = fields.Char(string="Promotion Percent")
    monthly_salary = fields.Float(related='job_title_degree_id.monthly_salary')
    minimum_allowance = fields.Float(related='job_title_degree_id.minimum_allowance')

    _sql_constraints = [
        ('Job_position_uniq', 'unique (name)',
         "The job position must be unique!")
    ]

    @api.onchange('job_title_degree_id', 'department_id')
    def compute_jop_position_name(self):
        for job in self:
            job_title = job.job_title_id.name if job.job_title_id.name else ''
            job_degree = job.job_degree if job.job_degree else ''
            job.name = " - ".join([job_title, job_degree])

    def _compute_job_count(self):
        """this function computes the number fo employees with this jop position"""
        for job in self:
            job.emp_no = self.env['hr.employee'].search_count([('job_id', '=', job.id)])


class HRJobFunctional(models.Model):
    _name = "hr.job.functional"
    _description = "Job Functional Groups"

    name = fields.Char(string="Job Functional Group", required=True)
    full_name = fields.Char(string="Job Full Name", compute='_compute_full_name')
    job_qualitative_ids = fields.One2many(comodel_name="hr.job.qualitative", inverse_name="job_functional_id",
                                          string="Job Qualitative Groups")
    emp_no = fields.Integer(string="Number of Employees", compute="_compute_emp_func_count")

    _sql_constraints = [
        ('Job_functional_uniq', 'unique (name)',
         "The functional group must be unique!")
    ]

    def _compute_full_name(self):
        for rec in self:
            rec.full_name = ' / '.join([rec.name])

    def _compute_emp_func_count(self):
        """this function computes the number fo employees with this functional group"""
        for func in self:
            job_list = self.env['hr.job'].search([('job_functional_id', '=', func.id)]).ids
            func.emp_no = self.env['hr.employee'].search_count([('job_id', 'in', job_list)])


class HRJobQualitative(models.Model):
    _name = "hr.job.qualitative"
    _description = "Job Qualitative Groups"

    job_functional_id = fields.Many2one('hr.job.functional', string="Job Functional Group", required=True)
    name = fields.Char(string="Job Qualitative Group", required=True)
    full_name = fields.Char(string="Job Full Name", compute='_compute_full_name')
    job_title_ids = fields.One2many(comodel_name="hr.job.title", inverse_name="job_qualitative_id", string="Job Titles")
    emp_no = fields.Integer(string="Number of Employees", compute="_compute_emp_qual_count")

    _sql_constraints = [
        ('Job_qualitative_uniq', 'unique (name, job_functional_id)',
         "The qualitative group should be unique for each functional group!")
    ]

    def _compute_full_name(self):
        for rec in self:
            rec.full_name = ' / '.join([rec.job_functional_id.name, rec.name])

    @api.onchange('job_functional_id')
    def onchange_job_functional_id(self):
        for rec in self:
            rec.name = False

    def _compute_emp_qual_count(self):
        """this function computes the number fo employees with this functional group"""
        for qual in self:
            job_list = self.env['hr.job'].search([('job_qualitative_id', '=', qual.id)]).ids
            qual.emp_no = self.env['hr.employee'].search_count([('job_id', 'in', job_list)])


class HRJobTitle(models.Model):
    _name = "hr.job.title"
    _description = "Job Title"

    job_functional_id = fields.Many2one('hr.job.functional', string="Job Functional Group", required=True)
    job_qualitative_id = fields.Many2one('hr.job.qualitative', string="Job Qualitative", required=True)
    name = fields.Char(string="Job Title", required=True)
    emp_no = fields.Integer(string="Number of Employees", compute="_compute_emp_title_count")
    full_name = fields.Char(string="Job Full Name", compute='_compute_full_name')
    job_degree_ids = fields.One2many(comodel_name='hr.job.degree', inverse_name='job_title_id', string="Job Degrees")

    _sql_constraints = [
        ('Job_title_uniq', 'unique (name, job_qualitative_id, job_functional_id)',
         'Job title should be unique for each qualitative group in each functional group!')
    ]

    def _compute_full_name(self):
        for rec in self:
            rec.full_name = ' / '.join([rec.job_functional_id.name, rec.job_qualitative_id.name, rec.name])

    @api.onchange('job_functional_id')
    def onchange_job_functional_id(self):
        for rec in self:
            rec.job_qualitative_id = False
            rec.name = False
            return {'domain': {'job_qualitative_id': [('job_functional_id', '=', rec.job_functional_id.id)]}}

    @api.onchange('job_qualitative_id')
    def onchange_job_qualitative_id(self):
        for rec in self:
            rec.name = False

    def _compute_emp_title_count(self):
        """this function computes the number fo employees with this job title"""
        for title in self:
            job_list = self.env['hr.job'].search([('job_title_id', '=', title.id)]).ids
            title.emp_no = self.env['hr.employee'].search_count([('job_id', 'in', job_list)])


class HRJobJobDegree(models.Model):
    _name = "hr.job.degree"
    _description = "HR Job Degree"

    def name_get(self):
        result = []
        for degree in self:
            name = degree.job_title_id.name + ' - ' + degree.name
            result.append((degree.id, name))
        return result

    job_functional_id = fields.Many2one('hr.job.functional', string="Job Functional Group", required=True)
    job_qualitative_id = fields.Many2one('hr.job.qualitative', string="Job Qualitative", required=True)
    job_title_id = fields.Many2one('hr.job.title', string="Job Title", required=True)
    financial_degree = fields.Selection(selection=[('first', 'First'), ('second', 'Second'), ('third', 'Third'),
                                                   ('forth', 'Forth'), ('fifth', 'Fifth'), ('sixth', 'Sixth'),
                                                   ('general_manager', 'General Manager'), ('highest', 'Highest'),
                                                   ('excellent', 'Excellent'), ('chief', 'Chief')],
                                        string="Financial Degree")
    name = fields.Char(string="Job Degree", required=True)
    full_name = fields.Char(string="Job Full Name", compute='_compute_full_name')
    emp_no = fields.Integer(string="Number of Employees", compute="_compute_emp_degree_count")
    monthly_salary = fields.Float(string="Job Salary")
    duration = fields.Integer(string="Duration")
    starting_degree_salary = fields.Float(string="Starting Degree Salary")
    minimum_allowance = fields.Float(string="Minimum Allowance")

    _sql_constraints = [
        ('Job_degree_uniq', 'unique (name, job_title_id, job_qualitative_id, job_functional_id)',
         'Job Degree should be unique for each job title in each qualitative group in each functional group!')
    ]

    def _compute_full_name(self):
        for rec in self:
            rec.full_name = ' / '.join(
                [rec.job_functional_id.name, rec.job_qualitative_id.name, rec.job_title_id.name, rec.name])

    @api.onchange('job_functional_id')
    def onchange_job_functional_id(self):
        for rec in self:
            rec.job_qualitative_id = False
            rec.job_title_id = False
            rec.name = False
            return {'domain': {'job_qualitative_id': [('job_functional_id', '=', rec.job_functional_id.id)]}}

    @api.onchange('job_qualitative_id')
    def onchange_job_qualitative_id(self):
        for rec in self:
            rec.job_title_id = False
            rec.name = False
            return {'domain': {'job_title_id': [('job_qualitative_id', '=', rec.job_qualitative_id.id)]}}

    @api.onchange('job_title_id')
    def onchange_job_title_id(self):
        for rec in self:
            rec.name = False

    def _compute_emp_degree_count(self):
        """this function computes the number fo employees with this job degree"""
        for degree in self:
            job_list = self.env['hr.job'].search([('job_title_degree_id', '=', degree.id)]).ids
            degree.emp_no = self.env['hr.employee'].search_count([('job_id', 'in', job_list)])
