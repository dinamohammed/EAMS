# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class penality_field(models.Model):
    _inherit = 'purchase.order'

    penality_perc = fields.Float(string='نسبة غرامة التأخير')
    down_payment_perc = fields.Float(string='نسبة الدفعة المقدمة')
    down_payment_total = fields.Float(compute='_compute_down_payment_total', string='الدفعة المقدمة')
    penality_value = fields.Float(string='غرامة التاخير')
    
    @api.depends('down_payment_perc','amount_total')
    def _compute_down_payment_total(self):
        perc = self.down_payment_perc / 100
        self.down_payment_total = (perc * self.amount_total)

    @api.depends('order_line.price_total','penality_perc')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
#           mentors start
            positeve_tax_amount = self.get_positve_amount(order)
            if  order.penality_perc > 0:
                percantage =  order.penality_perc / 100
                order.penality_value = (order.amount_untaxed + positeve_tax_amount) * percantage
                order.amount_total -= order.penality_value 
#           mentors end

    def get_positve_amount(self,order):
        tax_amounts = order.amount_by_group
        postive_tax_amount = 0
        for tax_amount in tax_amounts:
            if tax_amount[1] > 0 :
                postive_tax_amount += tax_amount[1] 

        return postive_tax_amount

