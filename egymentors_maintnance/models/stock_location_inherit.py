# -*- coding: utf-8 -*-

from odoo import fields, models


class LocationInherit(models.Model):
    _inherit = 'stock.location'

    maintenance_project_id = fields.Many2one(comodel_name="maintenance.project", string="Maintenance Project")
    maintenance_equipment_ids = fields.One2many(comodel_name='maintenance.project.equipment',
                                                inverse_name="stock_location_id", string="Maintenance Equipment")
    usage = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit Location'),
        ('maintenance', 'Maintenance Location')], string='Location Type',
        default='internal', index=True, required=True,
        help="* Vendor Location: Virtual location representing the source location for products coming from your vendors"
             "\n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products"
             "\n* Internal Location: Physical locations inside your own warehouses,"
             "\n* Customer Location: Virtual location representing the destination location for products sent to your customers"
             "\n* Inventory Loss: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)"
             "\n* Production: Virtual counterpart location for production operations: this location consumes the components and produces finished products"
             "\n* Transit Location: Counterpart location that should be used in inter-company or inter-warehouses operations")
