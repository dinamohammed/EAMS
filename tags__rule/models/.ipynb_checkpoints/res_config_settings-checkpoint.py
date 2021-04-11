from datetime import datetime

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    days_to_clear = fields.Date(string="Day to Clear Leaves per Employee")
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['days_to_clear'] = self.env['ir.config_parameter'].\
                                       get_param('days_to_clear', default= datetime.today())
        return res

    def set_values(self):
        self.days_to_clear and self.env['ir.config_parameter'].\
            set_param('days_to_clear', self.days_to_clear)
        super(ResConfigSettings, self).set_values()
