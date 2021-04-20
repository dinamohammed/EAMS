# -*- coding: utf-8 -*-
import base64
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval
from datetime import datetime
from collections import namedtuple


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    method = fields.Selection(string="Method", selection=[('gross', 'Gross'), ('net', 'Net')], required=True,
                              default='gross')
    hr_bonus_line_ids = fields.One2many(comodel_name='hr.bonus.line', inverse_name='payslip_id', string="Bonuses")
    hr_penalty_line_ids = fields.One2many(comodel_name='hr.penalty.line', inverse_name='payslip_id', string="Penalties")
    hr_trans_lines_ids = fields.One2many(comodel_name='hr.trans.allowance.line', inverse_name='payslip_id',
                                         string="Transportation Allowance")
    hr_award_profit_ids = fields.One2many(comodel_name='hr.award.profit.line', inverse_name='payslip_id',
                                          string="Award/Profit")
    total_bonus_ids = fields.One2many(comodel_name="hr.total.bonus", inverse_name="payslip_id", string="Bonus Totals",
                                      compute='_get_hr_bonuses', store=True)
    total_penalty_ids = fields.One2many(comodel_name="hr.total.penalty", inverse_name="payslip_id",
                                        string="Penalty Totals", compute='_get_hr_penalties', store=True)
    total_award_profit = fields.Float("Total Award/Profit", compute='_get_total_award_profit')
    total_award = fields.Float("Award", compute='_get_total_award_profit')
    total_profit = fields.Float("Profit", compute='_get_total_award_profit')

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if self.employee_id:
            super(HrPayslipInherit, self)._onchange_employee()
            self._get_hr_bonuses()
            self._get_hr_penalties()
            self._get_hr_trans_allowance()
            self._get_hr_award_profit()

    def _get_hr_bonuses(self):
        for payslip in self:
            bonus_line_obj = self.env['hr.bonus.line']
            domain = [('employee_id', '=', payslip.employee_id.id),
                      ('state', '=', 'confirm')]
            if payslip.date_from:
                domain.append(('date', '>=', payslip.date_from))
            if payslip.date_to:
                domain.append(('date', '<=', payslip.date_to))
            payslip.write({'hr_bonus_line_ids': [(6, 0, bonus_line_obj.search(domain).mapped('id'))]})
            if payslip.id or payslip._origin.id:
                self.compute_total_bonus(value=self)

    def _get_hr_penalties(self):
        penalty_line_obj = self.env['hr.penalty.line']
        for payslip in self:
            Range = namedtuple('Range', ['start', 'end'])
            range_1 = Range(
                start=datetime(payslip.date_from.year, payslip.date_from.month, payslip.date_from.day),
                end=datetime(payslip.date_to.year, payslip.date_to.month, payslip.date_to.day)
            )
            domain = ['|', ('date', '!=', False), ('date_to', '!=', False),
                      ('employee_id', '=', payslip.employee_id.id), ('state', '=', 'confirm')]
            penalties = penalty_line_obj.search(domain)
            penalty_line_ids = []
            for p_line in penalties:
                if p_line.date and p_line.date_to:
                    range_2 = Range(start=datetime(p_line.date.year, p_line.date.month, p_line.date.day),
                                    end=datetime(p_line.date_to.year, p_line.date_to.month, p_line.date_to.day))
                    latest_start = max(range_1.start, range_2.start)
                    earliest_end = min(range_1.end, range_2.end)
                    delta = (earliest_end - latest_start).days + 1
                    overlap = max(0, delta)
                    if overlap > 0:
                        penalty_line_ids.append(p_line.id)
            payslip.write({'hr_penalty_line_ids': [(6, 0, penalty_line_ids)]})
            if payslip.id or payslip._origin.id:
                self.compute_total_penalty(value=self)

    def _get_hr_trans_allowance(self):
        trans_line_obj = self.env['hr.trans.allowance.line']
        for payslip in self:
            domain = [('employee_id', '=', payslip.employee_id.id),
                      ('state', '=', 'confirm')]
            if payslip.date_from:
                domain.append(('date', '>=', payslip.date_from))
            if payslip.date_to:
                domain.append(('date', '<=', payslip.date_to))
            payslip.write({'hr_trans_lines_ids': [(6, 0, trans_line_obj.search(domain).mapped('id'))]})

    def _get_hr_award_profit(self):
        line_obj = self.env['hr.award.profit.line']
        for payslip in self:
            domain = [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'confirm')]
            if payslip.date_from:
                domain.append(('date', '>=', payslip.date_from))
            if payslip.date_to:
                domain.append(('date', '<=', payslip.date_to))
            payslip.write({'hr_award_profit_ids': [(6, 0, line_obj.search(domain).mapped('id'))]})

    @api.model
    def create(self, vals):
        contract_id = vals.get('contract_id')
        if contract_id and not vals.get('struct_id'):
            vals['struct_id'] = self.env['hr.contract'].browse(contract_id).structure_type_id.default_struct_id.id
        res = super(HrPayslipInherit, self).create(vals)
        res.compute_total_bonus(res)
        res.compute_total_penalty(res)
        return res

    def write(self, values):
        if values.get('employee_id', False):
            value = [self, values]
            self.compute_total_bonus(value=value, action='write')
            self.compute_total_penalty(value=value, action='write')
        return super(HrPayslipInherit, self).write(values)

    def compute_total_bonus(self, value, action=False):
        if action == 'write':
            payslip_id = value[1]['employee_id']
            value = value[0]
        else:
            payslip_id = value.id if value.id else value._origin.id
        for payslip in value:
            if payslip.employee_id:
                bonus_line_obj = self.env['hr.bonus.line']
                domain = [('employee_id', '=', payslip.employee_id.id),
                          ('state', '=', 'confirm')]
                if payslip.date_from:
                    domain.append(('date', '>=', payslip.date_from))
                if payslip.date_to:
                    domain.append(('date', '<=', payslip.date_to))
                grp_bonus_lines = bonus_line_obj.read_group(domain,
                                                            fields=['bonus_id', 'bonus_type_id', 'method',
                                                                    'amount:sum'],
                                                            groupby=['bonus_id', 'bonus_type_id', 'method'],
                                                            orderby="bonus_type_id, method",
                                                            lazy=False)
                payslip.total_bonus_ids = False
                total_list = []
                for total in grp_bonus_lines:
                    total_list.append((0, 0, {
                        'name': 'Payslip Total Bonus for: ' + payslip.name,
                        'payslip_id': payslip_id,
                        'bonus_id': total['bonus_id'][0],
                        'bonus_type_id': total['bonus_type_id'][0],
                        'method': total['method'],
                        'total': total['amount'],
                    }))
                payslip.total_bonus_ids = total_list

    def compute_total_penalty(self, value, action=False):
        if action == 'write':
            payslip_id = value[1]['employee_id']
            value = value[0]
        else:
            payslip_id = value.id if value.id else value._origin.id
        for payslip in value:
            if payslip.employee_id:
                penalty_line_obj = self.env['hr.penalty.line']
                domain = [('employee_id', '=', payslip.employee_id.id),
                          ('state', '=', 'confirm')]
                if payslip.date_from:
                    domain.append(('date', '>=', payslip.date_from))
                if payslip.date_to:
                    domain.append(('date', '<=', payslip.date_to))
                grp_penalty_lines = penalty_line_obj.read_group(domain,
                                                                fields=['penalty_id', 'penalty_type_id',
                                                                        'amount:sum'],
                                                                groupby=['penalty_id', 'penalty_type_id'],
                                                                orderby="penalty_type_id",
                                                                lazy=False)
                payslip.total_penalty_ids = False
                total_list = []
                for total in grp_penalty_lines:
                    total_list.append((0, 0, {
                        'name': 'Payslip Total Penalty for: ' + payslip.name,
                        'payslip_id': payslip_id,
                        'penalty_id': total['penalty_id'][0],
                        'penalty_type_id': total['penalty_type_id'][0],
                        'total': total['amount'],
                    }))
                payslip.total_penalty_ids = total_list

    def action_payslip_done(self):
        """
        Append Function to add extra action action_set_line_confirm
        :return: SUPER
        """
        lines_dicts = [{'lines': self.hr_bonus_line_ids, 'inverse_name': 'bonus_id'},
                       {'lines': self.hr_penalty_line_ids, 'inverse_name': 'penalty_id'},
                       {'lines': self.hr_award_profit_ids, 'inverse_name': 'award_profit_id'},
                       {'lines': self.hr_trans_lines_ids, 'inverse_name': 'trans_id'}]
        for lines_dict in lines_dicts:
            self.action_set_line_confirm(lines_dict)
        return super(HrPayslipInherit, self).action_payslip_done()

    def action_set_line_confirm(self, lines_dict):
        """
        Change State of this field lines to done to avoid using it on another payslip
        :param lines_dict: one2many field of those lines
        """
        for line in lines_dict['lines']:
            line.write({'state': 'done'})
            main_field = getattr(line, lines_dict['inverse_name'])
            if main_field._name == 'hr.bonus':
                if all(state == 'done' for state in main_field.bonus_line_ids.mapped('state')):
                    main_field.write({'state': 'done'})
            elif main_field._name == 'hr.penalty':
                if all(state == 'done' for state in main_field.penalty_line_ids.mapped('state')):
                    main_field.write({'state': 'done'})

    def default_action_payslip_done(self):
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state': 'done'})
        self.mapped('payslip_run_id').action_close()
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

    # Collect Report Data
    def get_salary_rules(self):
        salary_rules = []
        for payslip_id in self:
            for line in payslip_id.line_ids:
                if line.total and line.salary_rule_id.appears_on_payslip \
                        and line.salary_rule_id.id not in salary_rules:
                    salary_rules.append(line.salary_rule_id.id)
        return salary_rules

    def assign_parents_and_free_rules(self):
        """
        Get payslips rules and seprate them according to parent
        :return:
        - dict of parent and it's rules ids
        - list of rules ids which have no parents
        """
        salary_rules_obj = self.env['hr.salary.rule']
        salary_rules = self.get_salary_rules()
        salary_rule_ids = salary_rules_obj.browse(salary_rules).sorted(lambda l: l.sequence)
        salary_rule_parent = {}
        rules_without_parent = []
        for rule in salary_rule_ids:
            if rule.parent_id:
                if rule.parent_id.id in salary_rule_parent.keys():
                    # Parent Exist collect rules
                    if rule.id not in salary_rule_parent[rule.parent_id.id]:
                        salary_rule_parent[rule.parent_id.id].append(rule.id)
                else:
                    # new parent
                    salary_rule_parent[rule.parent_id.id] = [rule.id]
            else:
                # fill list of rules without parents
                rules_without_parent.append(rule.id)
        return salary_rule_parent, rules_without_parent

    def get_rule_parents_and_free(self, parent=False):
        """
        This will return object of parents and rules
        :param parent:
        :return:
        """
        salary_rule_parent_obj = self.env['hr.salary.rule.parent']
        salary_rules_obj = self.env['hr.salary.rule']
        salary_rule_parent, rules_without_parent = self.assign_parents_and_free_rules()
        parents = salary_rule_parent_obj.browse([r for r in salary_rule_parent])
        if parent:
            return parents.mapped('name')
        else:
            return salary_rules_obj.browse(rules_without_parent).mapped('name')

    def get_parent_amount(self, salary_rule_parent):
        payslip_line_obj = self.env['hr.payslip.line']
        list_of_totals = []
        for parent in salary_rule_parent:
            total = sum(l.total for l in payslip_line_obj.search([('salary_rule_id', 'in', salary_rule_parent[parent]),
                                                                  ('slip_id', 'in', self.ids)]))
            list_of_totals.append(round(total, 2))
        return list_of_totals

    def get_free_rule_amount(self, rules_without_parent):
        payslip_line_obj = self.env['hr.payslip.line']
        list_of_totals = []
        for rule in rules_without_parent:
            total = sum(l.total for l in payslip_line_obj.search([('salary_rule_id', '=', rule),
                                                                  ('slip_id', 'in', self.ids)]))
            list_of_totals.append(round(total, 2))
        return list_of_totals

    @api.onchange('hr_award_profit_ids')
    @api.depends('hr_award_profit_ids.amount')
    def _get_total_award_profit(self):
        for rec in self:
            rec.total_award_profit = sum(l.amount for l in rec.hr_award_profit_ids)
            rec.total_award = sum(l.amount for l in
                                  rec.hr_award_profit_ids.filtered(lambda x: x.award_profit_id.extra_type == 'award'))
            rec.total_profit = sum(l.amount for l in
                                   rec.hr_award_profit_ids.filtered(lambda x: x.award_profit_id.extra_type == 'profit'))

    # @api.onchange('hr_trans_lines_ids')
    # @api.depends('hr_trans_lines_ids.int_amount', 'hr_trans_lines_ids.ext_amount')
    # def _get_total_trans_allowance(self):
    #     for rec in self:
    #         rec.total_trans_allowance = sum(l.int_amount + l.ext_amount for l in rec.hr_trans_lines_ids)
    #         rec.total_trans_internal = sum(l.int_amount for l in rec.hr_trans_lines_ids)
    #         rec.total_trans_external = sum(l.ext_amount for l in rec.hr_trans_lines_ids)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    all_employees = fields.Boolean('All Employees', default=False)

    work_location_id = fields.Many2one('hr.location', "Work Location")
    company_id = fields.Many2one('res.company', string='Company')
    department_id = fields.Many2one('hr.department', "Department")
