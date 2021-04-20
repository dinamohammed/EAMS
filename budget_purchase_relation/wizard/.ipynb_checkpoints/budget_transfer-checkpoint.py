# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class BudgetTransfer(models.TransientModel):
    _name = 'budget.transfer'
    _description = 'Budget Transfer'
    
    name = fields.Char('Name')
    crossovered_budget_id = fields.Many2one('crossovered.budget','Budget', store = True)
    origin = fields.Char('Origin')
    budget_line_origin_id = fields.Many2one('crossovered.budget.lines','Budget Line origin')
    budget_line_dest_id = fields.Many2one('crossovered.budget.lines','Budget Line Destination')
    currency_id = fields.Many2one('res.currency', default = lambda self: self.env.company.currency_id , readonly=True)
    amount = fields.Monetary('Amount')
    
    @api.onchange('crossovered_budget_id')
    def onchange_crossovered_budget_id(self):
        if self.crossovered_budget_id:
#             raise ValidationError('%s'%self.budget_line_origin_id.crossovered_budget_id)
            if self.crossovered_budget_id != self.budget_line_origin_id.crossovered_budget_id \
                                and self.crossovered_budget_id != self.budget_line_dest_id.crossovered_budget_id:
                self.budget_line_origin_id = False
                self.budget_line_dest_id = False
            return {'domain': {
                'budget_line_origin_id': [('crossovered_budget_id', '=', self.crossovered_budget_id.id)],
                'budget_line_dest_id': [('crossovered_budget_id', '=', self.crossovered_budget_id.id)],
            }}
        
    
    def generate_transfer(self):
        create = False
        for line in self.crossovered_budget_id.crossovered_budget_line:
            if line.general_budget_id == self.budget_line_origin_id.general_budget_id:
                if line.planned_amount >= self.amount :
                    line.write({'planned_amount' : line.planned_amount - self.amount})
                    create = True
                else:
                    raise ValidationError("The amount is not avaialble in budgetary position")
            if line.general_budget_id == self.budget_line_dest_id.general_budget_id:
                line.write({'planned_amount' : line.planned_amount + self.amount})
                
        vals = {
            'name':self.name,
            'crossovered_budget_id':self.crossovered_budget_id.id,
            'origin':self.origin,
            'budget_line_origin_id':self.budget_line_origin_id.id,
            'budget_line_dest_id':self.budget_line_dest_id.id,
            'amount':self.amount,
        }
        if create == True :
            return self.env['crossovered.budget.transfer'].create(vals)