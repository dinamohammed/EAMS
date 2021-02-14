from odoo import models, fields

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_requisition_id = fields.Many2one('material.internal.requisition',string='Internal Requisition',readonly=True,copy=False)

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    custom_requisition_line_id = fields.Many2one('material.internal.requisition.line',string='Requisitions Line',copy=False)
