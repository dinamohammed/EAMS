# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
# Ahmed Salama Code Start ---->


class HrEmployeeConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    
    internal_static = fields.Float("Internal (Static)")
    internal_dynamic = fields.Float("Internal (Dynamic)")
    
    min_raise = fields.Float("Min Pay Raise")
    max_raise = fields.Float("Max Pay Raise")
    
    @api.model
    def get_values(self):
        res = super(HrEmployeeConfigSetting, self).get_values()
        res['internal_static'] = float(self.env['ir.config_parameter']. \
                                       get_param('internal_static', default=0.0))
        res['internal_dynamic'] = float(self.env['ir.config_parameter']. \
                                        get_param('internal_dynamic', default=0.0))
        res['min_raise'] = float(self.env['ir.config_parameter']. \
                                 get_param('min_raise', default=0.0))
        res['max_raise'] = float(self.env['ir.config_parameter']. \
                                 get_param('max_raise', default=0.0))
        return res
    
    def set_values(self):
        self.internal_static and self.env['ir.config_parameter']. \
            set_param('internal_static', self.internal_static)
        self.internal_dynamic and self.env['ir.config_parameter']. \
            set_param('internal_dynamic', self.internal_dynamic)
        self.min_raise and self.env['ir.config_parameter']. \
            set_param('min_raise', self.min_raise)
        self.max_raise and self.env['ir.config_parameter']. \
            set_param('max_raise', self.max_raise)
        super(HrEmployeeConfigSetting, self).set_values()

