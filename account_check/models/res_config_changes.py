# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class AccountCheckConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    
    check_validation = fields.Selection([('two', 'Two Steps'),
                                         ('three', 'Three Steps')],
                                        default='two', string="Check Validation",
                                        help="if we select three steps will effect in Customer payment cycle ")
    after_inbank = fields.Boolean("Full Cycle after Inbank")
    
    @api.model
    def get_values(self):
        res = super(AccountCheckConfigSetting, self).get_values()
        res.update(
            check_validation=self.env['ir.config_parameter'].get_param('check_validation', default='two'),
            after_inbank=self.env['ir.config_parameter'].get_param('after_inbank', False),
        )
        return res
    
    def set_values(self):
        super(AccountCheckConfigSetting, self).set_values()
        self.check_validation and self.env['ir.config_parameter']. \
            set_param('check_validation', self.check_validation)
        self.after_inbank and self.env['ir.config_parameter']. \
            set_param('after_inbank', self.after_inbank)
