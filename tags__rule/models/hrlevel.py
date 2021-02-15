# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLevel(models.Model):
    _inherit = 'hr.level'
    code = fields.Char(string="Level Code")

