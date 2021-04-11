# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    tender_request_id = fields.Many2one(comodel_name='tender.request', string="Tender Request")
