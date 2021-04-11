from odoo import models, fields


class Users(models.Model):
    _inherit = "res.users"

    tender_request_ids = fields.Many2many('tender.request', 'tender_request_rel', string='Tender Request')
