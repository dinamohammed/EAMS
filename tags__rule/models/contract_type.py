# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT , DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.safe_eval import safe_eval
import base64


    
class HrContactType(models.Model):
    _name = 'hr.contract.type'
    _inherit = ['mail.thread']
    _order = "name"


    
    name = fields.Char(string = "Contract Type" , required = True , store=True)
    code = fields.Char(string = "Contract Code" , required = True , store=True)

    