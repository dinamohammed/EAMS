# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    confirm_budget = fields.Boolean('Confirm Budget', default = False)
    budget_entry = fields.Many2one('budget.entry','Budget Entry')
    
    budgetary_amount = fields.Monetary(related = 'budget_id.total_available')
    
    def button_approve_budget(self):
        for record in self:
            for line in record.order_line:
                if record.budgetary_amount >= record.amount_total:
                    record.budget_id.approve_budget(record.amount_total, record.budget_id,
                                                line.budget_position_id, line.account_analytic_id)
                else:
                    raise ValidationError('No avaliable Budgetary amount')
            record.confirm_budget = True

                
    def button_confirm(self):
        for order in self:
            if order.budget_id and order.confirm_budget:
                continue
            elif order.budget_id and not order.confirm_budget:
                raise ValidationError('Need to Approve Budget first.')
            elif not order.budget_id and order.confirm_budget:
                continue
                
        return super(PurchaseOrder,self).button_confirm()
        

    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    budget_position_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    

    
    
class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"
    
    budget_type = fields.Selection([('reserve','Reserve'),
                                   ('expense','Expense')],
                                   string = 'Type', default='expense', required='True')
    currency_id = fields.Many2one(related = 'company_id.currency_id', readonly=True)

    total_available = fields.Monetary('Total Available', compute = '_compute_available_budget')
    
    def _compute_available_budget(self):
        for record in self:
            total = 0
            for line in record.crossovered_budget_line:
                total = line.available_amount + total
            record.total_available = total
    
    def approve_budget(self, amount_total, budget_id, budget_position_id, account_analytic_id):
        #### create budget entry ###
        for record in self:
            record.env['budget.entry'].create({'budget_id':budget_id,
                                            'budget_entry_type':'reserve',
                                            'state':'approved',
                                            'budget_allocation_ids':[(0,0,
                                                                      {'analytic_account_id':account_analytic_id.id,
                                                                      'general_budget_id':budget_position_id.id,
                                                                      'amount':amount_total,
                                                                      'budget_type':'reserve'})],})
    
    
class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    
    reserve_amount = fields.Monetary('Reserve Amount')
    commitment_amount = fields.Monetary('Commitment Amount')
    available_amount = fields.Monetary('Available Amount')
    
class BudgetEntry(models.Model):
    _name = "budget.entry"
    
    name = fields.Char('Entry Ref', required=True, index=True, copy=False, default='New', readonly=True)
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    
    date_budget = fields.Date('Date',default = datetime.today())
    
    budget_entry_type = fields.Selection([('budget','Budget'),
                                          ('reserve','Reserve'),
                                          ('commitment','Commitment'),
                                          ('budget_change','Budget Change')],
                                         string = 'Type', default='budget', required='True')
    
    state = fields.Selection([('draft','Draft'),
                             ('approved','Approved')], string = 'State', default = 'draft')
    
    budget_allocation_ids = fields.Many2many('budget.allocation', 'budget_entry_allocation_rel', 'budget_entry_id',
                                             'budget_allocation_id', 'Budget Allocations')
    
    def button_confirm(self):
        for record in self:
            if record.budget_entry_type == 'budget':
                ##### Add line in budget module
                for line in record.budget_allocation_ids:
                    record.budget_id.env['crossovered.budget.lines'].create({'general_budget_id':line.general_budget_id,
                                                                             'analytic_account_id':line.analytic_account_id,
                                                                             'start_date': line.start_date_budget,
                                                                             'end_date': line.end_date_budget,
                                                                             'available_amount':line.amount})
            record.write({'state':'approved'})
        
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_budget' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_budget']))
            vals['name'] = self.env['ir.sequence'].next_by_code('budget.entry', sequence_date=seq_date) or '/'
        return super(BudgetEntry, self).create(vals)

    
class BudgetAllocation(models.Model):
    _name = "budget.allocation"
    
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    
    start_date_budget = fields.Date('Start Date',default = datetime.strptime(str(datetime.today().year)+'-01-01',"%Y-%m-%d"))
    end_date_budget = fields.Date('End Date',default = datetime.strptime(str(datetime.today().year)+'-12-31',"%Y-%m-%d"))
    
    amount = fields.Float('Amount')
    currency_id = fields.Many2one('res.currency', default = lambda self: self.env.company.currency_id , readonly=True)
    
    requested_amount = fields.Monetary('Requested Amount')
    
    budget_type = fields.Selection([('reserve','Reserve'),
                                   ('expense','Expense'),
                                   ('budget','Budget')],
                                   string = 'Type', default='expense', required='True')
    
    
class AccountMove(models.Model):
    _inherit = "account.move"
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    
    
    
    
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    def _create_payments(self):
        
        
        
        return super(AccountPaymentRegister)._create_payments()