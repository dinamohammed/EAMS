# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EquipmentRequestInherit(models.Model):
    _inherit = 'maintenance.request'

    project_id = fields.Many2one(comodel_name="maintenance.project", string="Project Name")
    location_id = fields.Many2one(comodel_name="stock.location", string="Maintenance Location")
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Project Equipment")
    part_ids = fields.Many2many(comodel_name="maintenance.equipment.parts", string='Equipment Parts')
    task_sheet_line_ids = fields.One2many(comodel_name='maintenance.task.sheet.line', inverse_name='request_id',
                                          string="Task Sheet Lines")
    team_lead_id = fields.Many2one(related='maintenance_team_id.team_lead_id')

    @api.onchange('project_id')
    def onchange_project_id(self):
        for request in self:
            request.location_id = False
            request.equipment_id = False
            request.part_ids = False
            return {'domain': {
                'location_id': [('project_id', '=', request.project_id.id),
                                ('usage', '=', 'maintenance')],
                'equipment_id': [('location_id', '=', request.location_id.id)],
            }}

    @api.onchange('location_id')
    def onchange_location_id(self):
        for request in self:
            request.equipment_id = False
            request.part_ids = False
            return {'domain': {
                'equipment_id': [('location_id', '=', request.location_id.id)],
            }}

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        for request in self:
            request.part_ids = False
            return {'domain': {
                'part_ids': [('product_id', 'in', request.equipment_id.part_ids.mapped('product_id').ids)]
            }}


class MaintenanceTeamInherit(models.Model):
    _inherit = 'maintenance.team'

    team_lead_id = fields.Many2one(comodel_name='res.users', string="Team Lead")
