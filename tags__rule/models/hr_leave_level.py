# -*- coding: utf-8 -*-

from odoo import models, fields


class HrLeaveLevel(models.Model):
    _name = 'hr.leave.level'
    _description = 'Leaves Levels'
    
    name = fields.Char(string="Level Name")
    days = fields.Integer(string="Number of Leaves")
    years = fields.Integer(string="Number of Years")

