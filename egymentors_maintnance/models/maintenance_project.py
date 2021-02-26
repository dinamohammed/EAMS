# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceProject(models.Model):
    _name = "maintenance.project"
    _description = "Maintenance Project"

    name = fields.Char(string="Name")
    project_type_id = fields.Many2one(comodel_name='maintenance.project.type', string="Project Type")
    location_ids = fields.One2many(comodel_name='stock.location', inverse_name="project_id",
                                           string='Project Location')


class MaintenanceProjectType(models.Model):
    _name = "maintenance.project.type"
    _description = "Maintenance Project Type"

    name = fields.Char(sting="Name")


class LocationInherit(models.Model):
    _inherit = 'stock.location'

    project_id = fields.Many2one(comodel_name="maintenance.project", string="Maintenance Project")
    equipment_ids = fields.One2many(comodel_name='maintenance.equipment',
                                                inverse_name="location_id", string="Maintenance Equipment")
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

    @api.model
    def default_get(self, default_fields):
        res = super(LocationInherit, self).default_get(default_fields)
        if 'default_project_id' in self._context:
            res['project_id'] = self._context.get('default_project_id')
        return res


class ProjectEquipmentInherit(models.Model):
    _inherit = 'maintenance.equipment'

    project_id = fields.Many2one(comodel_name="maintenance.project", string="Project Name",
                                 related="location_id.project_id")
    location_id = fields.Many2one(comodel_name="stock.location", string="Maintenance Location",
                                  domain=[('usage', '=', 'maintenance'), ('project_id', '=', project_id)])
    part_ids = fields.One2many(comodel_name="maintenance.equipment.parts", inverse_name="equipment_id",
                               string="Equipment Part")
    task_ids = fields.One2many(comodel_name="maintenance.task.line", inverse_name="equipment_id", string="Tasks")

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            rec.location_id = False
            return {'domain': {'location_id': [('project_id', '=', rec.project_id.id),
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
                               related="product_id.categ_id",
                               help="Select category for the current product")
    project_id = fields.Many2one(comodel_name="maintenance.project", string="Project",
                                 related="equipment_id.project_id")
    location_id = fields.Many2one(comodel_name="stock.location", string="Location", related="equipment_id.location_id")
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipment")


class MaintenanceTaskLine(models.Model):
    _name = "maintenance.task.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Maintenance Task"

    name = fields.Char()
    project_id = fields.Many2one(comodel_name="maintenance.project", related='equipment_id.project_id')
    location_id = fields.Many2one(comodel_name="stock.location", related='equipment_id.location_id')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipment")
    task_id = fields.Many2one(comodel_name="maintenance.task", string="Maintenance Task", required=True)
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
