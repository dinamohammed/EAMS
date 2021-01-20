# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrTaxSlide(models.Model):
    _name = 'hr.tax.slide'
    # _inherit = 'hr.payslip'
    _description = "HR Tax Slide"
    _inherit = ['mail.thread', 'image.mixin']
    _order = 'priority'
    _check_company_auto = True

    name = fields.Char("Name", required=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id')
    max_amount = fields.Monetary("Max Amount", required=True, help='Lide max amount for this amount and below')
    active = fields.Boolean("Active", default=True)
    priority = fields.Integer(default=5, required=True,
                              help='The priority of the job, as an integer: 0 means higher priority,'
                                   ' 10 means lower priority.')
    line_ids = fields.One2many('hr.tax.slide.line', 'tax_slide_id', "Slice Components", required=True)
    _sql_constraints = [
        ('priority_unique', 'unique (name)', "priority already exists !"),
    ]

    @api.constrains('max_amount', 'priority')
    def _check_amount_with_priority(self):
        """
        Check if there is any below slides [With below priority] but with bigger amount
        :return:
        """
        for slc in self:
            if slc.max_amount and self.search([('priority', '<', slc.priority), ('max_amount', '>=', slc.max_amount)]):
                raise Warning(_("There are below slides [Priority less than %s] with bigger amount from [%s]"
                                " which against the logic!!!\n You can increase amount or handel priority")
                              % (slc.priority, slc.max_amount))

    def compute_tax_amount(self, amount):
        # print("HERE: ", amount, self)
        total_tax = 0.0
        for slide in self.sorted(lambda s: s.priority):
            # print("SLIDE: ", slide.max_amount)
            flag = False  # this flag will be raised if one of those slides worked
            if amount <= slide.max_amount:
                # print("--------- start ----------------")
                # start to process amount
                process_amount = amount
                slide_taxes = 0.0
                # print("process_amount: ", process_amount)
                for line in slide.line_ids:
                    # print("-------------\nCOND: ", line.amount_from, process_amount, line.amount_to)
                    if process_amount >= line.line_amount:
                        flag = True
                        tax = (line.line_amount * line.tax_percentage / 100)
                        # print("TAX: ", tax)
                        slide_taxes += tax
                        process_amount -= line.line_amount
                    else:
                        # print("--Last Tax--")
                        slide_taxes += (process_amount * line.tax_percentage / 100)
                        break
                total_tax += slide_taxes
                if flag:
                    break
        # print("total_tax: ", total_tax)
        return total_tax

# Tax Compute function
#     def taxesStageLoop(self, netSalary):
#         taxedAmount = netSalary
#         perRound = 0
#         if taxedAmount < self.max_amount:
#             for i in range(self.line_ids):
#                 if i == 0:
#                     if taxedAmount <= i.line_amount:
#                         taxedAmount = 0
#                         i.level = 0
#                         perRound = 0
#                     elif taxedAmount >= i.line_amount:
#                         taxedAmount = taxedAmount - i.line_amount
#                         i.level = 0
#                         perRound = 0
#                 elif i == 1:
#                     if taxedAmount >= i.line_amount:
#                         taxedAmount = taxedAmount - i.line_amount
#                         i.level = 1
#                         perRound = 1
#                 elif i == 2:
#                     if taxedAmount >= i.line_amount:
#                         taxedAmount = taxedAmount - i.line_amount
#                         i.level = 2
#                         perRound = 2
#                 elif i == 3:
#                     if taxedAmount >= i.line_amount:
#                         taxedAmount = taxedAmount - i.line_amount
#                         i.level = 3
#                         perRound = 3
#                 elif i == 4:
#                     if taxedAmount >= i.line_amount:
#                         taxedAmount = taxedAmount - i.line_amount
#                         i.level = 4
#                         perRound = 4
#                 elif i == 5:
#                     if taxedAmount >= i.line_amount:
#                         taxedAmount = taxedAmount - i.line_amount
#                         i.level = 5
#                         perRound = 5
#             taxedAmount = round(taxedAmount, 2)
#             return taxedAmount, perRound
#
#     def calculatedTotalTaxes(self ,taxedAmount , perRound):
#         tax = 0.00
#         if perRound == 0 and taxedAmount == 0:
#             tax = 0
#         elif perRound == 0 and taxedAmount != 0:
#             level = self.env['hr.tax.slide.line'].search([('level', '=', perRound+1)], limit=1)
#             tax = taxedAmount * (level.tax_percentage/100)
#         elif perRound == 1 and taxedAmount ==0:
#             level = self.env['hr.tax.slide.line'].search([('level','=',perRound)], limit=1)
#             tax = level.amount * (level.tax_percentage/100)
#         elif perRound == 1 and taxedAmount !=0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound+1)])
#             tax = level[1].amount * (level[1].tax_percentage/100) + taxedAmount * (level[2].tax_percentage/100)
#         elif perRound == 2 and taxedAmount ==0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound)])
#             tax = level[1].amount * (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100)
#         elif perRound == 2 and taxedAmount !=0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound+1)])
#             tax = level[1].amount* (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + taxedAmount * (level[3].tax_percentage/100)
#         elif perRound == 3 and taxedAmount == 0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound)])
#             tax = level[1].amount * (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + level[3].amount * (level[3].tax_percentage/100)
#         elif perRound == 3 and taxedAmount !=0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound + 1)])
#             tax = level[1].amount* (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + level[3].amount * (level[3].tax_percentage/100) + taxedAmount * (level[4].tax_percentage/100)
#         elif perRound == 4 and taxedAmount ==0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound)])
#             tax = level[1].amount* (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + level[3].amount * (level[3].tax_percentage/100) + level[4].amount * (level[4].tax_percentage/100)
#         elif perRound == 4 and taxedAmount !=0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound+1)])
#             tax = level[1].amount* (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + level[3].amount * (level[3].taxed_percentage/100) + level[4].amount * (level[4].taxed_percentage/100)+ taxedAmount * (level[5].tax_percentage/100)
#         elif perRound == 5 and taxedAmount ==0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound)])
#             tax = level[1].amount * (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + level[3].amount * (level[3].taxed_percentage/100) + level[4].amount * (level[4].taxed_percentage/100) + level[5].amount * level[5].tax_percentage
#         elif perRound == 5 and taxedAmount !=0:
#             level = self.env['hr.tax.slide.line'].search([('level', '<=', perRound+1)])
#             tax = level[1].amount * (level[1].tax_percentage/100) + level[2].amount * (level[2].tax_percentage/100) + level[3].amount * (level[3].tax_percentage/100) + level[4].amount * (level[4].tax_percentage/100) + level[5].amount * (level[5].tax_percentage/100) + taxedAmount * (level[6].tax_percentage/100)
#
#         return round(tax,2)


class HrTaxSlideLine(models.Model):
    _name = 'hr.tax.slide.line'
    _description = "HR Tax Slide Line"
    _order = 'amount_from, amount_to'

    tax_slide_id = fields.Many2one('hr.tax.slide', "Slide")
    amount_from = fields.Monetary("Amount From", required=True)
    amount_to = fields.Monetary("Amount To", required=True)
    line_amount = fields.Monetary("Amount", compute='_compute_line_amount')
    tax_percentage = fields.Float("Tax Percentage(%)", required=True)
    # level = fields.Integer("Tax Level")
    currency_id = fields.Many2one(related='tax_slide_id.currency_id')
    comment = fields.Text("Comment")

    @api.constrains('amount_from', 'tax_slide_id', 'amount_to')
    def _check_amount_with_priority(self):
        """
        Check if there is any below slides [With below priority] but with bigger amount
        :return:
        """
        for line in self:
            if line.tax_slide_id and (line.amount_from > line.tax_slide_id.max_amount
                                      or line.amount_to > line.tax_slide_id.max_amount):
                raise Warning(_("Line Amount couldn't exceed te slide max amount [%s]" % line.tax_slide_id.max_amount))

    @api.onchange('amount_from', 'amount_to')
    def _compute_line_amount(self):
        for line in self:
            line.line_amount = line.amount_to - line.amount_from
# Ahmed Salama Code E



