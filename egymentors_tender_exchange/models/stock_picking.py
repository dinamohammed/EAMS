from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tender_id = fields.Many2one('tender.request', string='Tender Request', readonly=True, copy=False)


class StockMove(models.Model):
    _inherit = 'stock.move'

    tender_request_line_id = fields.Many2one('tender.request.line', string='Tender Line', copy=False)
