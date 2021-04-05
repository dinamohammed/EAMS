# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    confirm_budget = fields.Boolean('Confirm Budget', default = False)
    reserve_budget_entry = fields.Many2one('budget.entry','Reserve Budget Entry', readonly = True)
    
    budgetary_amount = fields.Monetary(related = 'budget_id.total_available')
        
    def button_approve_budget(self):
        for record in self:
            for line in record.order_line:
                if record.budgetary_amount >= record.amount_total:
                    record.reserve_budget_entry = record.budget_id.approve_budget(record.amount_total, record.budget_id,
                                                line.budget_position_id, line.account_analytic_id)
                else:
                    raise ValidationError('No avaliable Budgetary amount')
            record.confirm_budget = True

                
    def button_confirm(self):
        for order in self:
            if order.budget_id and order.confirm_budget:
                continue
            elif order.budget_id and not order.confirm_budget:
#                 order.write({'budget_id': rec.budget_id.id})
#                 order.move_ids_without_package.write({'budget_id': rec.budget_id.id})
                raise ValidationError('Need to Approve Budget first.')
            elif not order.budget_id and order.confirm_budget:
                continue
                
        return super(PurchaseOrder,self).button_confirm()
        

    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    budget_position_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    
    budget_id = fields.Many2one(related='order_id.budget_id',store=True)
    
    reserve_budget_entry = fields.Many2one(related='order_id.reserve_budget_entry',store=True)
    
    def _prepare_account_move_line(self, move):
        res = super(PurchaseOrderLineInherit, self)._prepare_account_move_line(move)
        self.ensure_one()
        
        res['budget_id'] = self.order_id.budget_id.id
        res['reserve_budget_entry'] = self.order_id.reserve_budget_entry.id
        
        return res

    
    
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
            budget_entry = record.env['budget.entry'].create({'budget_id':budget_id.id,
                                                              'budget_entry_type':'reserve',
                                                              'state':'approved',
                                                              'budget_allocation_ids':[(0,0,
                                                                      {'analytic_account_id':account_analytic_id.id,
                                                                      'general_budget_id':budget_position_id.id,
                                                                      'amount':amount_total,
                                                                      'budget_type':'reserve'})],})
            return budget_entry

    
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
                    record.budget_id.write({'crossovered_budget_line' : [(0,0,
                                                                         {'general_budget_id':line.general_budget_id.id,
                                                                          'analytic_account_id':line.analytic_account_id.id,
                                                                          'date_from': line.start_date_budget,
                                                                          'date_to': line.end_date_budget,
                                                                          'available_amount':line.amount,
                                                                          'planned_amount':0.0})]})
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
    
    budget_id = fields.Many2one(related='invoice_line_ids.budget_id',store=True)
    
    reserve_budget_entry = fields.Many2one(related='invoice_line_ids.reserve_budget_entry',store=True)
    commitment_budget_entry = fields.Many2one(related='invoice_line_ids.reserve_budget_entry',store=True)
    

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    
    reserve_budget_entry = fields.Many2one('budget.entry','Reserve Budget Entry')
    commitment_budget_entry = fields.Many2one('budget.entry','Commitment Budget Entry')

    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super(AccountInvoiceInherit, self).create(vals_list)
        for move in moves:
            for line in move.line_ids:
                if line.purchase_line_id:
                    line['budget_id'] = line.purchase_line_id.budget_id.id
                    line['reserve_budget_entry'] = line.purchase_line_id.reserve_budget_entry.id
        return moves
    
    
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget',  readonly=True, copy=False)
    
    ####### Override method to add budget_id
    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'budget_id': self.line_ids[0].budget_id.id
        }
        
class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget',  readonly=True, copy=False)
    
    reserve_budget_entry = fields.Many2one('budget.entry','Reserve Budget Entry')
    
    commitment_budget_entry = fields.Many2one('budget.entry','Commitment Budget Entry')
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        payments = super(AccountPayment, self).create(vals_list)
        for payment in payments:
            if payment.move_id.budget_id:
                payment.write({'budget_id':payment.move_id.budget_id})
                payment.write({'reserve_budget_entry':payment.move_id.reserve_budget_entry})
                allocation_id = payment.reserve_budget_entry.budget_allocation_ids[0]
                payment.env['budget.entry'].create({'budget_id':payment.move_id.budget_id,
                                                    'budget_entry_type':'commitment',
                                                    'state':'approved',
                                                    'budget_allocation_ids':[(0,0,allocation_id,
                                                                    {
                                                                    'analytic_account_id':allocation_id.account_analytic_id.id,
                                                                    'general_budget_id':allocation_id.budget_position_id.id,
                                                                    'amount':payment.amount,
                                                                    'budget_type':'commitment'})],})
                
                line_id = payment.budget_id.crossovered_budget_line[0]
                available = line_id.available_amount - line.amount
                line_id.write({'available_amount':available})
                
        return payments