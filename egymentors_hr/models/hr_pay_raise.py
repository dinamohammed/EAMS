# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class HrPayRaise(models.Model):
    _name = 'hr.pay.raise'
    _description = "HR Pay Raise"
    _inherit = ['mail.thread', 'image.mixin']

    date = fields.Date("Date", default=fields.Date.today(),
                       readonly=True, states={'draft': [('readonly', False)]})
    name = fields.Char("Pay Raise",
                       readonly=True, states={'draft': [('readonly', False)]})
    contract_type_id = fields.Many2one('hr.contract.type', "Contract Type",
                                       readonly=True, states={'draft': [('readonly', False)]})
    percentage = fields.Float("Raise Percentage", readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float("Raise Amount", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')],
                             default='draft', string="Stage",
                             track_visibility='onchange', copy=False)
    line_ids = fields.One2many('hr.pay.raise.line', 'raise_id', "Pay Raises",
                               readonly=True, states={'draft': [('readonly', False)]})
    raise_type = fields.Selection(string="Raise Type", required=True,
                                  selection=[('amount', 'Fixed Amount'), ('percentage', 'Percentage')])

    def action_confirm(self):
        messages = ''
        for line in self.line_ids:
            new_salary = line.contract_id.wage + line.raise_amount
            if new_salary != line.contract_id.wage:
                messages += "- Employee [%s] Basic Salary [%s] updated to [%s] <br/>" % \
                            (line.employee_id.name, line.contract_id.wage, new_salary)
                line.employee_id.write({'previous_wage': line.contract_id.wage})
                line.contract_id.write({'wage': new_salary})
        if len(messages):
            self.message_post(body=messages)
        self.write({'state': 'confirm'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset(self):
        self.write({'state': 'draft'})

    def action_print_report(self):
        return self.env.ref('egymentors_hr.hr_pay_raise_report').report_action(self)

    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise Warning(_("You can't delete confirmed records!!!"))
        return super(HrPayRaise, self).unlink()


class HrPayRaiseLine(models.Model):
    _name = 'hr.pay.raise.line'
    _rec_name = 'raise_id'

    raise_id = fields.Many2one('hr.pay.raise', "Pay Raise")
    state = fields.Selection(related='raise_id.state')
    percentage = fields.Float(related='raise_id.percentage')
    amount = fields.Float(related='raise_id.amount')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
    contract_id = fields.Many2one('hr.contract', "Contract")
    employee_id = fields.Many2one(related='contract_id.employee_id')
    basic_salary = fields.Monetary(related='contract_id.wage', string="Basic Salary")
    raise_amount = fields.Monetary("Raise Amount", compute='_compute_line_raise', store=True)
    old_salary = fields.Monetary("Old Salary", track_visibility='onchange', compute='_compute_line_raise', store=True)
    new_salary = fields.Monetary("New Salary", track_visibility='onchange', compute='_compute_line_raise', store=True)

    @api.depends('contract_id', 'raise_id', 'raise_id.percentage', 'raise_id.amount', 'raise_id.raise_type')
    def _compute_line_raise(self, action=False):
        """
        This function compute the raise based on the raise type:
            first: Raise Amount: wage + raise_amount
            Second: wage * (raise_percentage / 100)
        Exception: According to the employee raise configurations, will apply any of the following:
            -If the raise is smaller than the Min Pay Raise, raise will be equal to Min Pay Raise
            -If the raise is bigger than the Max Pay Raise, raise will be equal to Max Pay Raise
        This function is computed if any of these fields is updated:
            contract_id - raise_id - raise_id.percentage - raise_id.amount - raise_id.raise_type
        """
        config_obj = self.env['ir.config_parameter'].sudo()
        min_raise = float(config_obj.get_param('min_raise', 0.0))
        max_raise = float(config_obj.get_param('max_raise', 0.0))
        raise_amount = 0
        for line in self:
            if line.contract_id and line.state not in ('confirm', 'done', 'cancel'):
                if line.raise_id.raise_type == 'amount':
                    raise_amount = line.raise_id.amount
                    line.raise_id.percentage = 0
                elif line.raise_id.raise_type == 'percentage':
                    raise_amount = (line.contract_id.wage * (line.raise_id.percentage / 100))
                    line.raise_id.amount = 0
                if min_raise > 0 and max_raise > 0:
                    if min_raise > raise_amount:
                        raise_amount = min_raise
                    elif max_raise < raise_amount:
                        raise_amount = max_raise
                line.write({'raise_amount': raise_amount})
                line.write({'old_salary': line.basic_salary})
                line.write({'new_salary': line.basic_salary + line.raise_amount})
