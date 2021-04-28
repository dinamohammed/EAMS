# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseFinancialRecord(models.Model):
    _name = "purchase.financial.record"
    _description = "Purchase Financial Record"

    requisition_id = fields.Many2one(comodel_name='purchase.requisition', readonly=True, string='Purchase Agreement')

    record_no = fields.Integer(string="Record Number")
    year = fields.Char(string="Year", default="2019/2020")
    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", default=lambda self: fields.Datetime.now())
    manager_id = fields.Many2one('hr.employee', string="Manager", required=True)
    job_title_id = fields.Many2one(related='manager_id.job_id')
    department_id = fields.Many2one(related='manager_id.job_department_id')

    signatures_financial_ids = fields.Many2many(related='requisition_id.signatures_ids')
    committee_reviewed = fields.Text(string="The committee has reviewed:")
    committee_recommend = fields.Text(string="The committee recommends:")

    def print_financial_record(self):
        return self.env.ref('egymentors_inventory.action_report_financial_record').report_action(self)


class PurchaseTechnicalRecord(models.Model):
    _name = "purchase.technical.record"
    _description = "Purchase Technical Record"

    requisition_id = fields.Many2one(comodel_name='purchase.requisition', readonly=True, string='Purchase Agreement')

    record_no = fields.Integer(string="Record Number")
    year = fields.Char(string="Year", default="2019/2020")
    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", default=lambda self: fields.Datetime.now())
    manager_id = fields.Many2one('hr.employee', string="Manager", required=True)
    job_title_id = fields.Many2one(related='manager_id.job_id')
    department_id = fields.Many2one(related='manager_id.job_department_id')

    signatures_technical_ids = fields.Many2many(related='requisition_id.signatures_technical_ids')
    committee_reviewed = fields.Text(string="The committee has reviewed:")
    committee_recommend = fields.Text(string="The committee recommends:")

    def print_technical_record(self):
        return self.env.ref('egymentors_inventory.report_technical_record').report_action(self)
