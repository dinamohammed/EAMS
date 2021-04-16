# -*- coding: utf-8 -*-

from odoo import fields, models


class AgreementSignature(models.Model):
    _name = 'agreement.signature'

    name = fields.Char(string="Name")
    title = fields.Char(string="Title")
    rank = fields.Integer('Rank', help="Add the Order of print out")


class AgreementSignatureTechnical(models.Model):
    _name = 'agreement.signature.technical'

    name = fields.Char(string="Name")
    title = fields.Char(string="Title")
    rank = fields.Integer('Rank', help="Add the Order of print out")
