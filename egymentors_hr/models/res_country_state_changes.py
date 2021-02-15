# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class ResCountryState(models.Model):
	_inherit = 'res.country.state'
	
	currency_id = fields.Many2one(related='country_id.currency_id')
	ext_amount = fields.Monetary("External Amount")

# Ahmed Salama Code End.
