# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EquipmentRequestInherit(models.Model):
    _inherit = 'maintenance.request'

    project_id = fields.Many2one(comodel_name="maintenance.project", string="Project Name")
    location_id = fields.Many2one(comodel_name="stock.location", string="Maintenance Location")
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Project Equipment")
    part_ids = fields.Many2many(comodel_name="maintenance.equipment.parts", string='Equipment Parts')

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            rec.location_id = False
            rec.equipment_id = False
            rec.part_ids = False
            return {'domain': {
                'location_id': [('project_id', '=', rec.project_id.id),
                                ('usage', '=', 'maintenance')],
                'equipment_id': [('location_id', '=', rec.location_id.id)],
            }}

    @api.onchange('location_id')
    def onchange_location_id(self):
        for rec in self:
            rec.equipment_id = False
            rec.part_ids = False
            return {'domain': {
                'equipment_id': [('location_id', '=', rec.location_id.id)],
            }}

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        for rec in self:
            rec.part_ids = False
            return {'domain': {'part_ids': [('id', '=', rec.equipment_id.id)]}}
