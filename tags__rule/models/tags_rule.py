# -*- coding: utf-8 -*-

import base64

from datetime import datetime

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.safe_eval import safe_eval


class TagsRule(models.Model):
    _inherit = 'hr.payslip'

    tax_base_temp = fields.Float(string='Tax Base Temp', default=0)

    def tags_function(self, category_ids):
        value = 0
        tag = []
        for category in category_ids:
            tag.append(category.name)
        return tag

    # ############### ############### ##################
    # To Execute the previous function on a salary rule :
    # Write the following code :
    #       result = payslip.env['hr.payslip'].tags_function(employee.category_ids)

    def date_error(self, specific_date):
        current_date = datetime.now()
        day_current_date = current_date.strftime("%d")
        specific_date_str = datetime.strptime(specific_date, DEFAULT_SERVER_DATE_FORMAT)
        day_specific_date = specific_date_str.strftime("%d")

        if day_specific_date < day_current_date:
            raise ValidationError(_('Sorry, Today Date Must be greater Than Start Date...'))

    # ############### ############### ##################
    # To Execute the previous function on a salary rule :
    # Write the following code :
    #       result = payslip.env['hr.payslip'].date_error('2019-1-12')

    def tax_base_value(self, tax_base, field_to_give):
        emp_rec = self.env['hr.employee'].search([('id', '=', field_to_give)])
        payslip_rec = self.env['hr.payslip'].search([('employee_id', '=', emp_rec['id']), ('state', '=', 'draft')])
        payslip_rec['tax_base_temp'] = tax_base

        return 0

    # ############### ############### ##################
    # To Execute the previous function on a salary rule :
    # Write the following code :
    #       result = payslip.env['hr.payslip'].tax_base_value(categories.RuleofTaxBase , employee.id)

    def action_payslip_done(self):
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state': 'done'})
        self.mapped('payslip_run_id').action_close()
        for payslip in self:
            # ##### Add the part of Tax Base Container
            payslip.employee_id.tax_base = payslip.tax_base_temp + payslip.employee_id.tax_base
            # ############### ##########################
        if self.env.context.get('payslip_generate_pdf'):
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                self.env['ir.attachment'].create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodestring(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })


class HrLevel(models.Model):
    _name = 'hr.level'

    name = fields.Char("Level")


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    location_type = fields.Selection([('static', 'Insured'),
                                      ('dynamic', 'Outside Insurance'),
                                      ('management', 'Non')], string="Insurance",
                                     required=True, default='static')

    tax_base = fields.Float(string='Tax Base', default=0)
    work_location_id = fields.Many2one('hr.location', 'Work Location Ertrac')
    certificate_id = fields.Many2one(comodel_name='hr.certificate', string="Certificate")

    def daily_check_value(self):

        current_date = datetime.now()
        if current_date.day == '30' or current_date.day == '31':
            emp_rec = self.env['hr.employee'].search([])
            for emp in emp_rec:
                emp['tax_base'] = 0

    # ############### ############### ############### ############### ################
    # Create A Scheduled Action :
    # Name : Update Tax Base Value
    # Model : Employee
    # Execute Every : 1 Week
    # Number of calls : -1
    # Action to Do : Execute Python Code
    # Code to write : Update Tax Base Value

    # ############### ############### ############### ############### #################
    # Add Fields to Employee Screen
    levels = fields.Selection([('level1', 'Level 1'),
                               ('level2', 'Level 2'),
                               ('level3', 'Level 3'),
                               ('level4', 'Level 4'),
                               ('level5', 'Level 5'),
                               ('level6', 'Level 6'),
                               ('level_dep_manager', 'Department Manager Level'),
                               ('level_sec_manager', 'Section Manager Level'),
                               ('level_sho2on_manager', 'Shoaon Manager Level')], string='Level')
    level_id = fields.Many2one('hr.level', "Level")

    certificate_level = fields.Selection([('diploma', 'Diploma'),
                                          ('bachelor', 'Bachelor'),
                                          ('license', 'License'),
                                          ('master', 'Master'),
                                          ('other', 'Other')], string='Certificate')

    grade_level = fields.Selection([('excellent', 'Excellent'),
                                    ('very_good', 'Very Good'),
                                    ('good', 'Good'),
                                    ('med', 'Med'),
                                    ('other', 'Other')], string='Grade Level')
    grade_year = fields.Char(string='Graduation Year')

    social_insurance_no = fields.Char(string='Social Insurance No.')
    insurance_date = fields.Date(string='Social Insurance Date')
    start_date = fields.Date(string='Social Insurance Start Date')
    end_date = fields.Date(string='Social Insurance End Date')
    medical_insurance_no = fields.Char(string='Medical Insurance No.')
    medical_location = fields.Char(string='Medical Location')

    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')

    military_service_status = fields.Selection([('exempted', 'Exempted'),
                                                ('postponed', 'Postponed'),
                                                ('completed', 'Completed')], string='Military Service Status')


class HrContractInherit(models.Model):
    _inherit = 'hr.contract'

    # ################## Contract Type # ##########################

    contract_type_id = fields.Many2one('hr.contract.type', 'Contract Type', store=True)

    # ####################### Allowance Fields # ############### ###############
    internal_transportation_value = fields.Float(string='Internal Transportation')
    veracity_value = fields.Float(string='Veracity')
    external_transportation_value = fields.Float(string='External Transportation')
    meal_value = fields.Float(string='Meal Voucher')
    rest_allowance = fields.Float(string='Rest Allowance')
    supervision_allowance = fields.Float(string='Supervision Allowance')
    allowance_1 = fields.Float(string='Allowance 1')
    allowance_2 = fields.Float(string='Allowance 2')
    allowance_3 = fields.Float(string='Allowance 3')
    allowance_4 = fields.Float(string='Allowance 4')
    allowance_5 = fields.Float(string='Allowance 5')
    allowance_6 = fields.Float(string='Allowance 6')
    allowance_7 = fields.Float(string='Allowance 7')
    allowance_8 = fields.Float(string='Allowance 8')
    allowance_9 = fields.Float(string='Allowance 9')
    allowance_10 = fields.Float(string='Allowance 10')
    allowance_11 = fields.Float(string='Allowance 11')
    allowance_12 = fields.Float(string='Allowance 12')
    allowance_13 = fields.Float(string='Allowance 13')
    allowance_14 = fields.Float(string='Allowance 14')
    allowance_15 = fields.Float(string='Allowance 15')
    allowance_16 = fields.Float(string='Allowance 16')
    allowance_17 = fields.Float(string='Allowance 17')
    allowance_18 = fields.Float(string='Allowance 18')
    allowance_19 = fields.Float(string='Allowance 19')
    allowance_20 = fields.Float(string='Allowance 20')
    allowance_21 = fields.Float(string='Allowance 21')
    allowance_22 = fields.Float(string='Allowance 22')
    allowance_23 = fields.Float(string='Allowance 23')

    # ####################### Deduction Fields # ############### ###############
    absence_value = fields.Float(string='Absence')
    house_deduction = fields.Float(string='House Deduction')
    deduction_1 = fields.Float(string='Deduction 1')
    deduction_2 = fields.Float(string='Deduction 2')
    deduction_3 = fields.Float(string='Deduction 3')
    deduction_4 = fields.Float(string='Deduction 4')
    deduction_5 = fields.Float(string='Deduction 5')
    deduction_6 = fields.Float(string='Deduction 6')
    deduction_7 = fields.Float(string='Deduction 7')
    deduction_8 = fields.Float(string='Deduction 8')
    deduction_9 = fields.Float(string='Deduction 9')
    deduction_10 = fields.Float(string='Deduction 10')
    deduction_11 = fields.Float(string='Deduction 11')
    deduction_12 = fields.Float(string='Deduction 12')
    deduction_13 = fields.Float(string='Deduction 13')
    deduction_14 = fields.Float(string='Deduction 14')
    deduction_15 = fields.Float(string='Deduction 15')
    deduction_16 = fields.Float(string='Deduction 16')
    deduction_17 = fields.Float(string='Deduction 17')
    deduction_18 = fields.Float(string='Deduction 18')
    deduction_19 = fields.Float(string='Deduction 19')
    deduction_20 = fields.Float(string='Deduction 20')
    deduction_21 = fields.Float(string='Deduction 21')
    deduction_22 = fields.Float(string='Deduction 22')
    deduction_23 = fields.Float(string='Deduction 23')
    deduction_24 = fields.Float(string='Deduction 24')
    deduction_25 = fields.Float(string='Deduction 25')
    deduction_26 = fields.Float(string='Deduction 26')
    deduction_27 = fields.Float(string='Deduction 27')
    deduction_28 = fields.Float(string='Deduction 28')
    deduction_29 = fields.Float(string='Deduction 29')
    deduction_30 = fields.Float(string='Deduction 30')
    deduction_31 = fields.Float(string='Deduction 31')
    deduction_32 = fields.Float(string='Deduction 32')
    deduction_33 = fields.Float(string='Deduction 33')
    deduction_34 = fields.Float(string='Deduction 34')
    deduction_35 = fields.Float(string='Deduction 35')
    deduction_36 = fields.Float(string='Deduction 36')
    deduction_37 = fields.Float(string='Deduction 37')
    deduction_38 = fields.Float(string='Deduction 38')

    allowance_ids = fields.One2many(comodel_name='hr.allowance', inverse_name='contract_id', string="Allowances")
    deduction_ids = fields.One2many(comodel_name='hr.deduction', inverse_name='contract_id', string="Deductions")

    # ############### ################ 7afeez --> Incentive # ############### ####################
    effort_allowance = fields.Float(string='Effort Allowance')
    manufacturing_allowance = fields.Float(string='Manufacturing Allowance')
    additional_allowance = fields.Float(string='Additional Allowance')
    ceo_allowance = fields.Float(string='CEO Allowance')
    traveling_days = fields.Integer(string='Traveling Days')
    transportation_expenses = fields.Float(string='Transportation Expenses')

    # ########################## Extra Fields Added #########################################
    security_days = fields.Integer(string='Security Days Allowance')
    company_pay = fields.Float(string='Company Pay')
    allowance_apecial = fields.Float(string='Special Allowance')
    total_institution_Value = fields.Float(string='Total Institutions Value')

    @api.model
    def create(self, vals):
        contracts = super(HrContractInherit, self).create(vals)
        if vals.get('employee_id'):
            other_contracts = self.env['hr.contract'].search([('employee_id', '=', vals.get('employee_id'))])
            if len(other_contracts) == 1:
                contracts.allowance_ids = [
                    (0, 0, {'allowance': self.env.ref('tags__rule.monthly_salary').id,
                            'value': contracts.job_id.monthly_salary}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.starting_degree_salary').id,
                            'value': contracts.job_id.starting_degree_salary}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_minimum').id,
                            'value': contracts.job_id.minimum_allowance}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_87_to_2009').id,
                            'value': contracts.job_id.starting_degree_salary * 275 / 100}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_66').id,
                            'value': 66}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_2011').id,
                            'value': contracts.job_id.starting_degree_salary * 10 / 100}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_2012').id,
                            'value': contracts.job_id.starting_degree_salary * 10 / 100}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_2013').id,
                            'value': contracts.job_id.starting_degree_salary * 10 / 100}),
                    (0, 0, {'allowance': self.env.ref('tags__rule.allowance_2014').id,
                            'value': contracts.job_id.starting_degree_salary * 10 / 100}),
                ]
        if vals.get('state') == 'open':
            contracts._assign_open_contract()
        open_contracts = contracts.filtered(
            lambda c: c.state == 'open' or c.state == 'draft' and c.kanban_state == 'done')
        # sync contract calendar -> calendar employee
        for contract in open_contracts.filtered(lambda c: c.employee_id and c.resource_calendar_id):
            contract.employee_id.resource_calendar_id = contract.resource_calendar_id
        return contracts

    def daily_check_contract_value(self):

        current_date = datetime.now()
        if current_date.day == '20':
            cont_rec = self.env['hr.contract'].search([])
            for cont in cont_rec:
                cont['security_days'] = 0
                cont['allowance_1'] = 0
                cont['deduction_3'] = 0
                cont['effort_allowance'] = 0
                cont['manufacturing_allowance'] = 0
                cont['additional_allowance'] = 0

    # ############### ############### ############### ############### ################
    # Create A Scheduled Action :
    # Name : Update Specific Values in
    # Model : Contract
    # Execute Every : 1 Week
    # Number of calls : -1
    # Action to Do : Execute Python Code
    # Code to write : Update Multi Contract Value


class HRAllowance(models.Model):
    _name = "hr.allowance"
    _description = "HR Allowance"
    _rec_name = 'allowance'

    allowance = fields.Many2one(comodel_name='hr.allowance.confg', string="Allowance")
    value = fields.Float(string="Value")
    contract_id = fields.Many2one(comodel_name='hr.contract', string="Contract")

    _sql_constraints = [
        ('allowance_uniq', 'unique (allowance,contract_id)',
         "The allowance must be unique!")
    ]


class HRDeduction(models.Model):
    _name = "hr.deduction"
    _description = "HR Deduction"

    deduction = fields.Many2one(comodel_name='hr.deduction.confg', string="Deduction")
    value = fields.Float(string="Value")
    contract_id = fields.Many2one(comodel_name='hr.contract', string="Contract")

    _sql_constraints = [
        ('deduction_uniq', 'unique (deduction,contract_id)',
         "The deduction must be unique!")
    ]


class HRAllowanceConfiguration(models.Model):
    _name = "hr.allowance.confg"
    _description = "HR Allowance Configuration"

    name = fields.Char(string="Allowance Name")
    code = fields.Char(string="Code")


class HRDeductionConfiguration(models.Model):
    _name = "hr.deduction.confg"
    _description = "HR Deduction Configuration"

    name = fields.Char(string="Deduction Name")
    code = fields.Char(string="Code")


class HRCertificate(models.Model):
    _name = "hr.certificate"
    _description = "HR Certificate"

    name = fields.Char(string="Name")

    _sql_constraints = [
        ('certificate_uniq', 'unique (name)', "The Certificate must be unique!")
    ]
