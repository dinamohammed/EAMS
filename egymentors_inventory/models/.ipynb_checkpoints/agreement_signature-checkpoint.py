# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class AgreementSignature(models.Model):
	_name = 'agreement.signature'
	
	name = fields.Many2one('hr.employee', 'Name')
	title = fields.Char(related = 'name.job_id.name', store=True)
	rank = fields.Integer('Rank',help="Add the Order of print out")
