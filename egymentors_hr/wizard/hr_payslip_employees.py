# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class HrPayslipEmployeesInherit(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    structure_id = fields.Many2one(required=True)
    
    def _get_available_contracts_domain(self):
        domain = super(HrPayslipEmployeesInherit, self)._get_available_contracts_domain()
        active_id = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        if active_id and active_id.work_location_id:
            domain.append(('work_location_id', '=', active_id.work_location_id.id))
        if active_id and active_id.all_employees:
            domain.append(('company_id', '=', active_id.company_id.id))
        if active_id and active_id.department_id:
            domain.append(('department_id', '=', active_id.department_id.id))
        return domain

# Ahmed Salama Code End.
