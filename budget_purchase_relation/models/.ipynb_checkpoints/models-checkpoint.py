# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    
    def button_approve(self):
        for record in self:
            pass
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    budget_position_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    

    
    
class CrossoveredBudget(models.Model):
    _inherit = "crossovered.budget"
    
    budget_type = fields.Selection([('reserve','Reserve'),
                                   ('expense','Expense')],
                                   string = 'Type', default='expense', required='True')
    
    
class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    
    reserve_amount = fields.Float('Reserve Amount')
    commitment_amount = fields.Float('Commitment Amount')
    available_amount = fields.Float('Available Amount')
    
class BudgetEntry(models.Model):
    _name = "budget.entry"
    
    name = fields.Char('Entry Ref', required=True, index=True, copy=False, default='New')
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    
    date_budget = fields.Date('Date',default = datetime.datetime.today())
    
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
        self.write({'state':'approved'})
        
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
    
    start_date_budget = fields.Date('Start Date',default = datetime.datetime.today())
    end_date_budget = fields.Date('End Date',default = datetime.datetime.today())
    
    amount = fields.Float('Amount')
    
    budget_type = fields.Selection([('reserve','Reserve'),
                                   ('expense','Expense'),
                                   ('budget','Budget')],
                                   string = 'Type', default='expense', required='True')
    
    

