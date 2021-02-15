# -*- coding: utf-8 -*-

import base64

from datetime import datetime

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.safe_eval import safe_eval


class HrContract(models.Model):
    _inherit = 'hr.contract'

    employee_no = fields.Char(string = 'Employee Registration Number',search = '_get_search_list',store = False)

    def _get_search_list(self,operator,value):
        #print("------------------- On Search List -----------------")
        #print("VALS:: ",operator,value )
        if operator == 'like':
            operator = 'ilike'
        employee_ids = self.env['hr.employee'].search([('registration_number',operator,value)]).mapped('id')
        #print("Employee Ids:: ", employee_ids)
        contract_ids = self.env['hr.contract'].search([('employee_id','in',employee_ids)]).mapped('id')
        #ids = values
        #print("Contract Ids:: ", contract_ids)
        return [('id','in',contract_ids)]


class HrPayslip(models.Model):
      _inherit = 'hr.payslip'

      employee_no = fields.Char(string = 'Employee Registration Number',search = '_get_search_list',store = False)

      def _get_search_list(self,operator,value):
           #print("------------------- On Search List -----------------")
           #print("VALS:: ",operator,value )
           if operator == 'like':
               operator = 'ilike'
           employee_ids = self.env['hr.employee'].search([('registration_number',operator,value)]).mapped('id')
           #print("Employee Ids:: ", employee_ids)
           payslip_ids = self.env['hr.payslip'].search([('employee_id','in',employee_ids)]).mapped('id')
           #ids = values
           #print("Contract Ids:: ", payslip_ids)
           return [('id','in',payslip_ids)]


