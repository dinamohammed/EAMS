# -*- coding: utf-8 -*-
from odoo import models, fields


class HRContractInherit(models.Model):
    _inherit = 'hr.contract'

    job_functional_id = fields.Many2one(related='job_id.job_functional_id')
    job_qualitative_id = fields.Many2one(related='job_id.job_qualitative_id')
    job_title_id = fields.Many2one(related='job_id.job_title_id')
    job_degree = fields.Char(related='job_id.job_degree')

    department_id = fields.Many2one(related='job_id.department_id')

    financial_degree = fields.Char(related='job_id.financial_degree')
    starting_degree_salary = fields.Float(related='job_id.starting_degree_salary')
    duration = fields.Integer(related='job_id.duration')
    promotion_percent = fields.Char(related='job_id.promotion_percent')
    monthly_salary = fields.Float(related='job_id.monthly_salary')
