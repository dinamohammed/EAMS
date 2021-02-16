# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class JobPosition(models.Model):
    _inherit = 'hr.job'

    # functional_job_id = fields.Many2one('hr.functional.job', string="Functional Job Group", required=True)
    # qualitative_job_id = fields.Many2one('hr.qualitative.job', string="Qualitative Jobs", required=True)
    job_title_id = fields.Many2one('hr.title', string="Job Title", required=True)
    name = fields.Char(string='Job Position', required=False, index=True, translate=True)
    emp_no = fields.Integer()

    _sql_constraints = [
        ('Job_position_uniq', 'unique (qualitative_job_id, qualitative_job_id, job_title_id)',
         'يجب أن يكون المسمي الوظيفي فريدًا في المجموعة الوظيفية في المجموعة النوعية!')
    ]

    def _compute_emp_dep_count(self):
        """this function computes the number fo employees within the department"""
        for dep in self:
            dep.emp_no = self.env['hr.employee'].search_count([('department_id', '=', dep.id)])


class FunctionalJob(models.Model):
    _name = "hr.functional.job"
    _description = "Functional Job Groups"

    name = fields.Char(string="Functional Job Group", required=True)
    qualitative_job_ids = fields.One2many(comodel_name="hr.qualitative.job", inverse_name="functional_job_id",
                                          string="Qualitative Job Groups")

    _sql_constraints = [
        ('Job_title_uniq', 'unique (name)',
         'يجب أن تكون المجموعة الوظيفية فريدة!')
    ]


class QualitativeJob(models.Model):
    _name = "hr.qualitative.job"
    _description = "Qualitative Job Groups"

    functional_job_id = fields.Many2one('hr.functional.job', string="Functional Job Group", required=True)
    name = fields.Char(string="Qualitative Job Group", required=True)
    job_title_ids = fields.One2many(comodel_name="hr.title", inverse_name="qualitative_job_id", string="Job Titles")

    _sql_constraints = [
        ('Job_title_uniq', 'unique (name, functional_job_id)',
         'يجب أن تكون المجموعة النوعية فريدة لكل مجموعة وظيفية!')
    ]


class JobTitle(models.Model):
    _name = "hr.title"
    _describtion = "Job Title"

    functional_job_id = fields.Many2one('hr.functional.job', string="Functional Job Group", required=True)
    qualitative_job_id = fields.Many2one('hr.qualitative.job', string="Qualitative Jobs", required=True)
    name = fields.Char(string="Job Title", required=True)
    emp_no = fields.Integer(compute="_compute_emp_dep_count")
    job_full_name = fields.Char(string="Job Full Name", compute='_compute_job_full_name')

    def _compute_job_full_name(self):
        for rec in self:
            rec.job_full_name = ' / '.join([rec.functional_job_id.name, rec.qualitative_job_id.name, rec.name])

    @api.onchange('functional_job_id')
    def onchange_functional_job_id(self):
        for rec in self:
            rec.qualitative_job_id = False
            # rec.job_title_id = False
            return {'domain': {'qualitative_job_id': [('functional_job_id', '=', rec.functional_job_id.id)]}}

    @api.onchange('qualitative_job_id')
    def onchange_qualitative_job_id(self):
        for rec in self:
            # rec.job_title_id = False
            return {'domain': {'job_title_id': [('qualitative_job_id', '=', rec.qualitative_job_id.id)]}}

    # @api.onchange('job_title_id')
    # def onchange_job_title_id(self):
    #     for rec in self:
    #         if rec.job_title_id.functional_job_id.name and rec.job_title_id.qualitative_job_id.name and rec.job_title_id.name:
    #             job_name = ' / '.join(
    #                 [rec.job_title_id.functional_job_id.name, rec.job_title_id.qualitative_job_id.name,
    #                  rec.job_title_id.name])
    #             rec.name = job_name

    def _compute_emp_dep_count(self):
        """this function computes the number fo employees within the department"""
        for dep in self:
            dep.emp_no = self.env['hr.employee'].search_count([('department_id', '=', dep.id)])

    # _sql_constraints = [
    #     ('Job_title_uniq', 'unique (name, qualitative_job_id, functional_job_id)',
    #      'يجب أن يكون المسمي الوظيفي فريدًا لكل مجموعة نوعية في كل مجموعة وظيفية!')
    # ]


class JobCareer(models.Model):
    _name = "hr.career"
    _description = "HR Career"

    name = fields.Char(string="Career")
    functional_job_id = fields.Many2one('hr.functional.job', string="Functional Job Group")
    hierarchical_order_id = fields.Many2one('hr.hierarchical.order', string="Hierarchical Order")


class HierarchicalOrder(models.Model):
    _name = "hr.hierarchical.order"
    _description = "Hierarchical Order"

    name = fields.Char(string="Hierarchical Order")
    degree = fields.Integer(string="Job Degree")
    duration = fields.Integer(string="Duration")
    financial_rank = fields.Char(string="Financial Rank")
