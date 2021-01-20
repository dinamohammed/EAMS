# -*- coding: utf-8 -*-
from odoo import models, fields, api


# Ahmed Salama Code Start ---->


class HrContractInherit(models.Model):
	_inherit = 'hr.contract'

	analytic_tag_id = fields.Many2one('account.analytic.tag', "Analytic Tags")

	@api.depends('employee_id', 'name')
	@api.depends('employee_id.name')
	def name_get(self):
		result = []
		for contract_id in self:
			name = contract_id.name if contract_id.name == contract_id.employee_id.name \
				else "%s - %s" % (contract_id.employee_id.name, contract_id.name)
			result.append((contract_id.id, name))
		return result
	

# Ahmed Salama Code End.
