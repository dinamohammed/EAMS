# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EquipmentRequestInherit(models.Model):
    _inherit = 'maintenance.request'

    maintenance_project_id = fields.Many2one(comodel_name="maintenance.project", string="Project Name")
    stock_location_id = fields.Many2one(comodel_name="stock.location", string="Maintenance Location")
    project_equipment_id = fields.Many2one(comodel_name="maintenance.project.equipment", string="Project Equipment")
    equipment_part_ids = fields.Many2many(comodel_name="maintenance.equipment.parts", string='Equipment Parts')

    @api.onchange('maintenance_project_id')
    def onchange_maintenance_project_id(self):
        for rec in self:
            rec.stock_location_id = False
            rec.project_equipment_id = False
            rec.equipment_part_ids = False
            return {'domain': {
                'stock_location_id': [('maintenance_project_id', '=', rec.maintenance_project_id.id),
                                      ('usage', '=', 'maintenance')],
                'project_equipment_id': [('stock_location_id', '=', rec.stock_location_id.id)],
            }}

    @api.onchange('stock_location_id')
    def onchange_stock_location_id(self):
        for rec in self:
            rec.project_equipment_id = False
            rec.equipment_part_ids = False
            return {'domain': {
                'project_equipment_id': [('stock_location_id', '=', rec.stock_location_id.id)],
            }}

    @api.onchange('project_equipment_id')
    def onchange_project_equipment_id(self):
        for rec in self:
            rec.equipment_part_ids = False
            return {'domain': {'equipment_part_ids': [('id', '=', rec.project_equipment_id.id)]}}
