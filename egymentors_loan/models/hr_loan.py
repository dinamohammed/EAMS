# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
# Ahmed Salama Code Start ---->


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            ts_user_id = result['user_id']
        else:
            ts_user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search([('user_id', '=', ts_user_id)], limit=1).id
        return result

    def _compute_loan_amount(self):
        total_paid = 0.0
        for loan in self:
            for line in loan.line_ids:
                if line.paid:
                    total_paid += line.amount
            balance_amount = loan.loan_amount - total_paid
            loan.total_amount = loan.loan_amount
            loan.balance_amount = balance_amount
            loan.total_paid_amount = total_paid

    name = fields.Char(string="Loan Name", default="/", readonly=True, help="Name of the loan")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True, help="Date")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, help="Employee")
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,
                                    string="Department", help="Employee")
    months = fields.Integer(string="No Of Months", default=1, help="Number of months")
    payment_date = fields.Date(string="Payment Start Date", required=True,
                               default=fields.Date.today(), help="Date of the payment")
    line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True, help="Company",
                                 default=lambda self: self.env.user.company_id,
                                 states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    job_position = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True, string="Job Position",
                                   help="Job position")
    loan_amount = fields.Float(string="Loan Amount", required=True, help="Loan amount")
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_loan_amount',
                                help="Total loan amount")
    balance_amount = fields.Float(string="Balance Amount", compute='_compute_loan_amount', help="Balance amount")
    total_paid_amount = fields.Float(string="Total Paid Amount", compute='_compute_loan_amount',
                                     help="Total paid amount")
    notes = fields.Text("Notes")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
    ], string="State", default='draft', track_visibility='onchange', copy=False, )

    @api.model
    def create(self, values):
        loan_count = self.env['hr.loan'].search_count(
            [('employee_id', '=', values['employee_id']), ('state', '=', 'approve'),
             ('balance_amount', '!=', 0)])
        if loan_count:
            raise ValidationError(_("The employee has already a pending months"))
        else:
            values['name'] = self.env['ir.sequence'].get('hr.loan.seq') or ' '
            res = super(HrLoan, self).create(values)
            return res

    def compute_months(self):
        """This automatically create the months the employee need to pay to
        company based on payment start date and the no of months.
            """
        for loan in self:
            loan.line_ids.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.months
            for i in range(1, loan.months + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
        return True

    def action_refuse(self):
        return self.write({'state': 'refuse'})

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        for data in self:
            if not data.line_ids:
                raise ValidationError(_("Please Compute Months"))
            else:
                self.write({'state': 'approve'})

    def unlink(self):
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(
                    'You cannot delete a loan which is not in draft or cancelled state')
        return super(HrLoan, self).unlink()


class LoanMonthLine(models.Model):
    _name = "hr.loan.line"
    _description = "Month Line"

    date = fields.Date(string="Payment Date", required=True, help="Date of the payment")
    employee_id = fields.Many2one('hr.employee', string="Employee", help="Employee")
    amount = fields.Float(string="Amount", required=True, help="Amount")
    paid = fields.Boolean(string="Paid", help="Paid")
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.", help="Loan")
    payslip_id = fields.Many2one('hr.payslip', string="Payslip Ref.", help="Payslip")
    
# Ahmed Salama Code End.
