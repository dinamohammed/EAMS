# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    budget_id = fields.Many2one('crossovered.budge', 'Budget')
    

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    budget_position_id = fields.Many2one('account.budge.post', 'Budgetary Position')

