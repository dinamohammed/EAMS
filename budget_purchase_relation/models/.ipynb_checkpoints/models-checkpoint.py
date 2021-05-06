# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    confirm_budget = fields.Boolean('Confirm Budget', default = False, copy=False)
    reserve_budget_entry = fields.Many2one('budget.entry','Reserve Budget Entry', readonly = True, copy=False)
    
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
    
    def _prepare_account_move_line(self):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line()
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
    
    budget_transfer = fields.Selection([('current','Current'),
                                   ('investment','Investment')],
                                   string = 'Transfer/Account Type', default='current', required='True')

    total_available = fields.Monetary('Total Available', compute = '_compute_available_budget')
    
    budget_division_id = fields.Many2one('budget.division', string= 'Budget Division')
    
    @api.onchange('budget_division_id')
    def _add_budget_positions(self):
        for record in self:
            record.crossovered_budget_line.unlink()
            if record.budget_division_id.general_budget_ids:
                for budget in record.budget_division_id.general_budget_ids:
#                     vals =  {'general_budget_id':budget.id,
#                              'date_from':record.date_from,
#                              'date_to': record.date_to,}
#                     record.update({'crossovered_budget_line':[(0,0,vals)]})
                    for account in record.budget_division_id.analytic_account_ids:
                        vals =  {'general_budget_id':budget.id,
                                 'date_from':record.date_from,
                                 'date_to': record.date_to,
                                 'analytic_account_id':account.id,}
                        record.update({'crossovered_budget_line':[(0,0,vals)]})
            elif record.budget_division_id.analytic_account_ids:
                for account in record.budget_division_id.analytic_account_ids:
                    vals =  {'analytic_account_id':account.id,
                             'date_from':record.date_from,
                             'date_to': record.date_to,}
                    record.update({'crossovered_budget_line':[(0,0,vals)]})
                    
#     @api.onchange('budget_division_id')
#     def _add_budget_positions(self):
#         vals = {}
#         for record in self:
#             record.crossovered_budget_line.unlink()
#             if record.budget_division_id.general_budget_ids:
#                 if record.budget_division_id.analytic_account_ids:
#                     for id , budget in enumerate(record.budget_division_id.general_budget_ids):
# #                         raise ValidationError('%s'%record.budget_division_id.analytic_account_ids[id].name)
#                         vals =  {'general_budget_id':budget.id,
#                                  'date_from':record.date_from,
#                                  'date_to': record.date_to,
#                                 'analytic_account_id': record.budget_division_id.analytic_account_ids[id],}
#                         record.update({'crossovered_budget_line':[(0,0,vals)]})
#             elif record.budget_division_id.analytic_account_ids:
#                 for account in record.budget_division_id.analytic_account_ids:
#                     vals['analytic_account_id'] = account.id
#                     record.update({'crossovered_budget_line':[(0,0,vals)]})
    
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
        
        
    transfers_count = fields.Integer(compute='compute_count')
    
    def compute_count(self):
        for record in self:
            record.transfers_count = self.env['crossovered.budget.transfer'].search_count([('crossovered_budget_id', '=', self.id)])
            
    def get_transfers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfers',
            'view_mode': 'tree',
            'res_model': 'crossovered.budget.transfer',
            'domain': [('crossovered_budget_id', '=', self.id)],
            'context': "{'create': False}"
        }

    
class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"
    
    dependable_amount = fields.Monetary('dependable')
    reserve_amount = fields.Monetary('Reserve Amount')
    commitment_amount = fields.Monetary('Commitment Amount')
    available_amount = fields.Monetary('Available Amount')
    
    budget_transfer = fields.Selection(related="crossovered_budget_id.budget_transfer")
    
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
                                   ('budget','Budget'),
                                   ('commitment','Commitment')],
                                   string = 'Type', default='expense', required='True')
    
    
class AccountMove(models.Model):
    _inherit = "account.move"
    
    budget_id = fields.Many2one(related='invoice_line_ids.budget_id',store=True)
    
    reserve_budget_entry = fields.Many2one(related='invoice_line_ids.reserve_budget_entry',store=True)
    commitment_budget_entry = fields.Many2one(related='invoice_line_ids.commitment_budget_entry',store=True)
    
    
    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        moves = super(AccountMove, self).create(vals_list)
        for move in moves:
            for line in move.line_ids:
                if line.purchase_line_id:
                    line['budget_id'] = line.purchase_line_id.budget_id.id
                    line['reserve_budget_entry'] = line.purchase_line_id.reserve_budget_entry.id
        return moves
    

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    
    reserve_budget_entry = fields.Many2one('budget.entry','Reserve Budget Entry')
    commitment_budget_entry = fields.Many2one('budget.entry','Commitment Budget Entry')

    
    
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    
    budget_id = fields.Many2one('crossovered.budget', 'Budget',  readonly=True, copy=False)
    reserve_budget_entry = fields.Many2one('budget.entry','Reserve Budget Entry')
    
        ####### Override method to add budget_id

    def _create_payment_vals_from_wizard(self):
        # OVERRIDE
        payment_vals = super()._create_payment_vals_from_wizard()
        payment_vals['budget_id'] = self.line_ids[0].move_id.budget_id.id
        payment_vals['reserve_budget_entry'] = self.line_ids[0].move_id.reserve_budget_entry.id
#         raise ValidationError('wait - %s'%self.line_ids[0].move_id.reserve_budget_entry)
        return payment_vals
        
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
            if payment.budget_id:
                payment.write({'budget_id':payment.budget_id})
                payment.write({'reserve_budget_entry':payment.reserve_budget_entry})
#                 raise ValidationError('%s'%payment.reserve_budget_entry.budget_allocation_ids)
                allocation_id = payment.reserve_budget_entry.budget_allocation_ids[0]
                payment.env['budget.entry'].create({'budget_id':payment.budget_id,
                                                    'budget_entry_type':'commitment',
                                                    'state':'approved',
                                                    'budget_allocation_ids':[(0,0,{
                                                                    'analytic_account_id':allocation_id.analytic_account_id.id,
                                                                    'general_budget_id':allocation_id.general_budget_id.id,
                                                                    'amount': -allocation_id.amount,
                                                                    'budget_type':'reserve'}),
                                                                             (0,0,{
                                                                    'analytic_account_id':allocation_id.analytic_account_id.id,
                                                                    'general_budget_id':allocation_id.general_budget_id.id,
                                                                    'amount':payment.amount,
                                                                    'budget_type':'commitment'})]})
                
                line_id = payment.budget_id.crossovered_budget_line[0]
                available = line_id.available_amount - payment.amount
                line_id.write({'available_amount':available})
                
        return payments


#     def payment_budget_vals(self,payment):
#         raise ValidationError('%s'%payment.move_id.budget_id)
#         if payment.move_id.budget_id:
#                 payment.write({'budget_id':payment.move_id.budget_id})
#                 payment.write({'reserve_budget_entry':payment.move_id.reserve_budget_entry})
#                 allocation_id = payment.reserve_budget_entry.budget_allocation_ids[0]
#                 payment.env['budget.entry'].create({'budget_id':payment.move_id.budget_id,
#                                                     'budget_entry_type':'commitment',
#                                                     'state':'approved',
#                                                     'budget_allocation_ids':[(0,0,allocation_id,
#                                                                     {
#                                                                     'analytic_account_id':allocation_id.account_analytic_id.id,
#                                                                     'general_budget_id':allocation_id.budget_position_id.id,
#                                                                     'amount':payment.amount,
#                                                                     'budget_type':'commitment'})],})
                
#                 line_id = payment.budget_id.crossovered_budget_line[0]
#                 available = line_id.available_amount - line.amount
#                 line_id.write({'available_amount':available})
        
    
#     @api.model_create_multi
#     def create(self, vals_list):
#         # OVERRIDE
#         write_off_line_vals_list = []

#         for vals in vals_list:

#             # Hack to add a custom write-off line.
#             write_off_line_vals_list.append(vals.pop('write_off_line_vals', None))

#             # Force the move_type to avoid inconsistency with residual 'default_move_type' inside the context.
#             vals['move_type'] = 'entry'

#             # Force the computation of 'journal_id' since this field is set on account.move but must have the
#             # bank/cash type.
#             if 'journal_id' not in vals:
#                 vals['journal_id'] = self._get_default_journal().id

#             # Since 'currency_id' is a computed editable field, it will be computed later.
#             # Prevent the account.move to call the _get_default_currency method that could raise
#             # the 'Please define an accounting miscellaneous journal in your company' error.
#             if 'currency_id' not in vals:
#                 journal = self.env['account.journal'].browse(vals['journal_id'])
#                 vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id

#         payments = super().create(vals_list)

#         for i, pay in enumerate(payments):
#             write_off_line_vals = write_off_line_vals_list[i]

#             # Write payment_id on the journal entry plus the fields being stored in both models but having the same
#             # name, e.g. partner_bank_id. The ORM is currently not able to perform such synchronization and make things
#             # more difficult by creating related fields on the fly to handle the _inherits.
#             # Then, when partner_bank_id is in vals, the key is consumed by account.payment but is never written on
#             # account.move.
#             to_write = {'payment_id': pay.id}
#             for k, v in vals_list[i].items():
#                 if k in self._fields and self._fields[k].store and k in pay.move_id._fields and pay.move_id._fields[k].store:
#                     to_write[k] = v

#             if 'line_ids' not in vals_list[i]:
#                 to_write['line_ids'] = [(0, 0, line_vals) for line_vals in pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

#             pay.move_id.write(to_write)
            
#             pay.payment_budget_vals(pay)

#         return payments


class BudgetDivision(models.Model):
    _name = "budget.division"
    _description = "Abwab"
    
    name = fields.Char('Name', required = True)
    code = fields.Char('Code')
    main_division_bool = fields.Boolean('Main Division', help = "Check if the division is main , uncheck if the division is Sub,"
                                   "used for reporting purpose")
    general_budget_ids = fields.One2many('account.budget.post','budget_division_id', 'Budgetary Position')
    
    main_division = fields.Many2one('budget.division', string= 'Parent Division')
    
    budget_transfer = fields.Selection([('current','Current'),
                                   ('investment','Investment')],
                                   string = 'Transfer/Account Type', default='current')
    analytic_account_ids = fields.One2many('account.analytic.account','budget_division_id', 'Analytic Account')
    

class AccountBudgetPost(models.Model):
    _inherit = "account.budget.post"
    
    budget_division_id = fields.Many2one('budget.division', string= 'Budget Division')
    
class CrossoveredBudgetTransfer(models.Model):
    _name = "crossovered.budget.transfer"
    _description = "Transfers Budget"
    
    
    name = fields.Char('Name')
    crossovered_budget_id = fields.Many2one('crossovered.budget','Budget')
    origin = fields.Char('Origin')
    budget_line_origin_id = fields.Many2one('crossovered.budget.lines','Budget Line origin')
    budget_line_dest_id = fields.Many2one('crossovered.budget.lines','Budget Line Destination')
    currency_id = fields.Many2one('res.currency', default = lambda self: self.env.company.currency_id , readonly=True)
    amount = fields.Monetary('Amount')
    
    

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    
    budget_division_id = fields.Many2one('budget.division', string= 'Budget Division')