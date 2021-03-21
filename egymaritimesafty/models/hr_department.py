# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _translate = False

    emp_no = fields.Integer(compute='_compute_emp_dep_count')

    def _compute_emp_dep_count(self):
        """this function computes the number fo employees within the department"""
        for dep in self:
            dep.emp_no = self.env['hr.employee'].search_count([('department_id', '=', dep.id)])
