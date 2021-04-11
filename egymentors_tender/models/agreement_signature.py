# -*- coding: utf-8 -*-

from odoo import fields, models


class AgreementSignature(models.Model):
    _name = 'agreement.signature'

    name = fields.Many2one('hr.employee', 'Name')
    title = fields.Char(related='name.job_id.name', store=True)
    rank = fields.Integer('Rank', help="Add the Order of print out")


class AgreementSignatureTender(models.Model):
    _name = 'agreement.signature.tender'

    name = fields.Char(string="Name")
    title = fields.Char(string="Title")
    rank = fields.Integer('Rank', help="Add the Order of print out")
