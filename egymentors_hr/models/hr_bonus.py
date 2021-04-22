# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_STATES = [('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')]


class HRBonus(models.Model):
    _name = 'hr.bonus'
    _description = 'HR Bonus'
    _inherit = ['mail.thread', 'image.mixin']

    name = fields.Char(string="Name", translate=True, required=True)
    bonus_categ_id = fields.Many2one(comodel_name="hr.bonus.categ", string="Bonus Category")
    date = fields.Date(string="Date", default=fields.Date.today(), readonly=True,
                       states={'draft': [('readonly', False)]})
    period_month = fields.Char(string="Period Month", default=lambda x: fields.Date.today().strftime("%B"),
                               readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')
    bonus_line_ids = fields.One2many(comodel_name="hr.bonus.line", inverse_name="bonus_id", string="Bonus Lines",
                                     readonly=True, states={'draft': [('readonly', False)]})
    total_bonus_ids = fields.One2many(comodel_name="hr.total.bonus", inverse_name="bonus_id", string="Bonus Totals",
                                      compute='_compute_total_bonus', store=True)

    @api.depends('bonus_line_ids')
    def _compute_total_bonus(self):
        """
        This function computes group of totals based on the bonus type and the method used in the bonus line.
        """
        if self.bonus_line_ids:
            for rec in self:
                grp_bonus_lines = self.env['hr.bonus.line'].read_group([('bonus_id', '=', rec.id)],
                                                                       fields=['bonus_type_id', 'method', 'amount:sum'],
                                                                       groupby=['bonus_type_id', 'method'],
                                                                       orderby="bonus_type_id desc, method desc",
                                                                       lazy=False)
                rec.total_bonus_ids = False
                val = []
                for total in grp_bonus_lines:
                    val.append((0, 0, {
                        'name': 'Total Bonus: ' + rec.name,
                        'bonus_id': rec._origin.id,
                        'bonus_type_id': total['bonus_type_id'][0],
                        'method': total['method'],
                        'total': total['amount'],
                    }))
                rec.total_bonus_ids = val

    def action_confirm(self):
        """
        This function calls `_change_state` that changes the state to be "Confirmed".
        """
        for action in self:
            action._change_state('confirm')

    def _change_state(self, state):
        """
         This function changes the state of the line to be as given in the parameter.
        :param state: The state of the line that will be changed to.
        """
        self.write({'state': state})
        for line in self.bonus_line_ids:
            line.write({
                'state': state,
                'name': 'Bonus Line: ' + self.name,
            })

    def action_print_report(self):
        """
        This function prints the bonus report.
        """
        return self.env.ref('egymentors_hr.hr_bonus_report').report_action(self)

    def action_cancel(self):
        """
        This function cancels the bonus by calling the function `_change_state` and changes the state to cancel.
        """
        for action in self:
            action._change_state('cancel')

    def unlink(self):
        """
        This function unlink the bonus, but if the state of the bonus is confirmed, it will raise warning.
        """
        for rec in self:
            if rec.state == 'confirm':
                raise ValidationError(_("You can't delete confirmed records!!!"))
        return super(HRBonus, self).unlink()

    def action_reset(self):
        """
        This function reset the bonus and changes its state to draft.
        :return:
        """
        for action in self:
            action._change_state('draft')


class HRBonusLine(models.Model):
    _name = 'hr.bonus.line'
    _description = 'HR Bonus Line'

    name = fields.Char(string="Name")
    bonus_id = fields.Many2one(comodel_name='hr.bonus', string="Bonus")
    payslip_id = fields.Many2one(comodel_name='hr.payslip', string="Payslip")
    date = fields.Date(related='bonus_id.date', string="Date")
    employee_id = fields.Many2one(comodel_name='hr.employee', string="Employee", required=True)
    bonus_type_id = fields.Many2one(comodel_name='hr.bonus.type', string="Type", required=True)
    method = fields.Selection(string="Method", selection=[('gross', 'Gross'), ('net', 'Net')], required=True,
                              default='gross')
    amount = fields.Float(string="Amount")
    notes = fields.Text(string="Notes")
    state = fields.Selection(_STATES, default='draft', string="Stage", track_visibility='onchange')


class HRBonusType(models.Model):
    _name = 'hr.bonus.type'
    _description = 'HR Bonus Type'

    name = fields.Char(string="Name", required=True)
    bonus_categ_id = fields.Many2one(comodel_name="hr.bonus.categ", string="Bonus Category", required=True)
    code = fields.Char(string="Code", required=True, )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "A bonus type with the same name already exists."),
        ('code_uniq', 'unique (code)', "A bonus type with the same code already exists."),
    ]


class HRBonusCategory(models.Model):
    _name = 'hr.bonus.categ'
    _description = 'HR Bonus Category'

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "A category with the same name already exists."),
    ]


class HRTotalBonus(models.Model):
    _name = 'hr.total.bonus'
    _description = 'New Description'
    _order = "bonus_type_id, method"

    name = fields.Char(string="Name", required=True)
    bonus_id = fields.Many2one(comodel_name='hr.bonus', string="Bonus", ondelete='cascade')
    payslip_id = fields.Many2one(comodel_name='hr.payslip', string="Payslip")
    method = fields.Selection(string="Method", selection=[('gross', 'Gross'), ('net', 'Net')], required=True,
                              default='gross')
    bonus_type_id = fields.Many2one(comodel_name='hr.bonus.type', string="Bonus Type", required=True)
    total = fields.Float(string="Total")
