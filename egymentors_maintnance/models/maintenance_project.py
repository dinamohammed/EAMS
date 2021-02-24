# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceProject(models.Model):
    _name = "maintenance.project"
    _description = "Maintenance Project"

    name = fields.Char(string="Name")
    project_type_id = fields.Many2one(comodel_name='maintenance.project.type', string="Project Type")
    project_location_ids = fields.One2many(comodel_name='stock.location', inverse_name="maintenance_project_id",
                                           string='Project Location')


class MaintenanceProjectType(models.Model):
    _name = "maintenance.project.type"
    _description = "Maintenance Project Type"

    name = fields.Char(sting="Name")


class ProjectEquipment(models.Model):
    _name = 'maintenance.project.equipment'
    _description = "Maintenance Project Equipment"

    name = fields.Char(sting="Name")
    maintenance_project_id = fields.Many2one(comodel_name="maintenance.project", string="Project Name")
    stock_location_id = fields.Many2one(comodel_name="stock.location", string="Maintenance Location",
                                        domain=[('usage', '=', 'maintenance'),
                                                ('maintenance_project_id', '=', maintenance_project_id)])
    equipment_part_ids = fields.Many2many(comodel_name="maintenance.equipment.parts", string="Equipment Part")
    task_ids = fields.One2many(comodel_name="maintenance.task.line", inverse_name="equipment_id", string="Tasks")

    @api.onchange('maintenance_project_id')
    def onchange_maintenance_project_id(self):
        for rec in self:
            rec.stock_location_id = False
            return {'domain': {'stock_location_id': [('maintenance_project_id', '=', rec.maintenance_project_id.id),
                                                     ('usage', '=', 'maintenance')]}}


class EquipmentParts(models.Model):
    _name = 'maintenance.equipment.parts'
    _description = 'Equipment Parts'
    _rec_name = 'product_id'

    @api.onchange('product_id')
    def _product_qty(self):
        self.product_stock = self.product_id.qty_available

    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float(string="Quantity")
    product_stock = fields.Float(string="Product Stock")
    categ_id = fields.Many2one(comodel_name='product.category', string='Product Category',
                               help="Select category for the current product")


class MaintenanceTaskLine(models.Model):
    _name = "maintenance.task.line"
    _description = "Maintenance Task"

    name = fields.Char()
    # project_id = fields.Many2one(comodel_name="stock.location", related='equipment_id.maintenance_project_id')
    # location_id = fields.Many2one(comodel_name="stock.location", related='equipment_id.stock_location_id')
    equipment_id = fields.Many2one(comodel_name="maintenance.project.equipment", string="Equipment")
    task_id = fields.Many2one(comodel_name="maintenance.task", string="Maintenance Task")
    date = fields.Date(default=fields.Date.today(), string='Date')
    state = fields.Selection(string="State", selection=[('yes', 'Yes'), ('no', 'No')])
    note = fields.Text()
    task_categ_id = fields.Many2one(comodel_name="task.categ", string="Task Category")


class MaintenanceTask(models.Model):
    _name = "maintenance.task"
    _description = "Maintenance Task"

    name = fields.Char()


class TaskCategory(models.Model):
    _name = "task.categ"
    _description = "Task Category"

    name = fields.Char(string="Name")
