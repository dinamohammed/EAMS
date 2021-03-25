# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MaintenanceProject(models.Model):
    _name = "maintenance.project"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Maintenance Project"

    name = fields.Char(string="Name", required=True)
    project_type_id = fields.Many2one(comodel_name='maintenance.project.type', string="Project Type")
    location_ids = fields.One2many(comodel_name='stock.location', inverse_name="project_id",
                                   string='Project Location')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Project Name must be unique.')
    ]


class MaintenanceProjectType(models.Model):
    _name = "maintenance.project.type"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Maintenance Project Type"

    name = fields.Char(sting="Name", required=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Project Type must be unique.')
    ]


class LocationInherit(models.Model):
    _name = 'stock.location'
    _inherit = ['stock.location', 'mail.thread', 'mail.activity.mixin']

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
    category_id = fields.Many2one(comodel_name='maintenance.equipment.category', string='Equipment Category',
                                  tracking=True, group_expand='_read_group_category_ids', required=True)
    equipment_type = fields.Many2one(comodel_name='maintenance.equipment.type', string="Equipment Type")

    brand = fields.Char(string="Brand")
    country_id = fields.Many2one(string="Country of Origin", comodel_name='res.country')
    engine_type = fields.Char(string="Engine type")
    generator_type = fields.Char(string="Generator Type")
    electrical_capacity = fields.Char(string="Electrical Capacity")
    number_facets = fields.Integer(string="Number of facets")
    speed = fields.Integer(string="Speed")
    cooling_type = fields.Char(string="Cooling type")
    installation_date = fields.Date(string="Installation Date")
    cooling_capacity = fields.Char(string="Cooling Capacity")
    device_type = fields.Char(string="Device type")
    power_factor = fields.Char(string="Power Factor")
    efficiency = fields.Char(string="Efficiency")
    consumed_electrical_power = fields.Char(string="Consumed Electrical Power")
    lantern_char = fields.Char(string="Lantern type and characteristic")
    navigational_range = fields.Char(string="Navigational Range")
    number_of_tier = fields.Integer(string="Number of Tier")
    skew_angle = fields.Char(string="Skew Angle")
    ip_protection_factor = fields.Char(string="IP Protection Factor")
    type = fields.Char(string="Type")
    number_of_matrices = fields.Integer(string="Number of matrices")
    capacity = fields.Integer(string="Capacity")
    code = fields.Char(string="Code")
    location_Technical_condition = fields.Char(string="Location Technical Condition")

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            rec.location_id = False
            return {'domain': {'location_id': [('project_id', '=', rec.project_id.id),
                                               ('usage', '=', 'maintenance')]}}


class EquipmentParts(models.Model):
    _name = 'maintenance.equipment.parts'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Equipment Parts'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float(string="Quantity")
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

    name = fields.Char(string="Name", required=True)
    project_id = fields.Many2one(comodel_name="maintenance.project", related='equipment_id.project_id')
    location_id = fields.Many2one(comodel_name="stock.location", related='equipment_id.location_id')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipment")
    task_categ_id = fields.Many2one(comodel_name="maintenance.task.categ", string="Task Category", required=True)
    task_id = fields.Many2one(comodel_name="maintenance.task", string="Maintenance Task", required=True)

    @api.onchange('task_categ_id')
    def onchange_task_categ_id(self):
        for task in self:
            task.task_id = False
            return {'domain': {
                'task_id': [('task_categ_id', '=', task.task_categ_id.id)]
            }}

    @api.onchange('task_id')
    def onchange_task_id(self):
        for task in self:
            if task.task_id:
                task.name = "Equipment Task: " + task.task_id.name


class MaintenanceTaskCategory(models.Model):
    _name = "maintenance.task.categ"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Task Category"

    name = fields.Char(string="Name", required=True)
    task_ids = fields.One2many(comodel_name="maintenance.task", inverse_name="task_categ_id", string="Tasks")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Task Category must be unique.')
    ]


class MaintenanceTask(models.Model):
    _name = "maintenance.task"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = "Maintenance Task"

    name = fields.Char(string="Task", required=True)
    task_categ_id = fields.Many2one(comodel_name="maintenance.task.categ", string="Task Category", required=True)
    equipment_ids = fields.Many2many(comodel_name='maintenance.equipment', string="Equipments",
                                     compute='_compute_equipments')

    _sql_constraints = [
        ('name_uniq', 'unique (name, task_categ_id)', 'Task Name and Task Category must be unique.')
    ]

    def _compute_equipments(self):
        task_line_obj = self.env['maintenance.task.line']
        for task in self:
            task.equipment_ids = task_line_obj.search([('task_id', '=', task.id)]).mapped('equipment_id')


class MaintenanceTaskSheet(models.Model):
    _name = "maintenance.task.sheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Maintenance Task Sheet"

    name = fields.Char(string="Name", required=True, default="Task Sheet: ")
    project_ids = fields.Many2many(comodel_name="maintenance.project", string="Project", required=True)
    location_ids = fields.Many2many(comodel_name="stock.location", string="Location")
    equipment_ids = fields.Many2many(comodel_name="maintenance.equipment", string="Equipment")
    task_categ_ids = fields.Many2many(comodel_name="maintenance.task.categ", string="Task Category")
    task_sheet_line_ids = fields.One2many(comodel_name="maintenance.task.sheet.line", inverse_name="task_sheet_id",
                                          string="Task Sheet Line")
    technical_status_ids = fields.One2many(comodel_name="maintenance.technical.status", inverse_name="task_sheet_id",
                                           string="Task Sheet Line")

    _sql_constraints = [
        ('name', "CHECK(name)", "Task Sheet name cannot be duplicated."),
    ]

    @api.onchange('project_ids')
    def onchange_project_ids(self):
        for task in self:
            task.location_ids = False
            task.equipment_ids = False
            task.task_categ_ids = False
            return {'domain': {
                'location_ids': [('project_id', '=', task.project_ids.ids),
                                 ('usage', '=', 'maintenance')]
            }}

    @api.onchange('location_ids')
    def onchange_location_ids(self):
        for task in self:
            task.equipment_ids = False
            task.task_categ_ids = False
            return {'domain': {
                'equipment_ids': [('location_id', '=', task.location_ids.ids)],
            }}

    @api.onchange('equipment_ids')
    def onchange_equipment_ids(self):
        task_sheet_line_obj = self.env['maintenance.task.sheet.line']
        for task in self:
            task.task_categ_ids = False
            task_sheet_lines = task_sheet_line_obj.search([('equipment_id', 'in', task.equipment_ids.ids)])
            return {'domain': {
                'task_categ_ids': [('id', 'in', task_sheet_lines.mapped('task_categ_id').ids)],
            }}

    @api.onchange('project_ids', 'location_ids', 'equipment_ids', 'task_categ_ids')
    def compute_task_sheet_lines_domain(self):
        domain = []
        task_line_obj = self.env['maintenance.task.line']
        for task_sheet in self:
            if task_sheet.project_ids:
                if task_sheet.project_ids or task_sheet.location_ids or task_sheet.equipment_ids or task_sheet.task_categ_ids:
                    if not task_sheet.name:
                        raise ValidationError(_("Please define Task sheet name."))
                    if task_sheet.project_ids:
                        domain.append(('project_id', 'in', task_sheet.project_ids.ids))
                    if task_sheet.location_ids:
                        domain.append(('location_id', 'in', task_sheet.location_ids.ids))
                    if task_sheet.equipment_ids:
                        domain.append(('equipment_id', 'in', task_sheet.equipment_ids.ids))
                    if task_sheet.task_categ_ids:
                        domain.append(('task_categ_id', 'in', task_sheet.task_categ_ids.ids))

                    task_lines = task_line_obj.search(
                        domain, order='project_id ASC, location_id ASC, equipment_id ASC, task_categ_id ASC'
                    )

                    task_sheet.task_sheet_line_ids = False
                    for task_line in task_lines:
                        task_sheet.task_sheet_line_ids.create({
                            'name': 'Task sheet line :' + task_sheet.name,
                            'task_sheet_id': task_sheet.id,
                            'task_line_id': task_line.id,
                        })

                    task_sheet.technical_status_ids = False
                    equip_list = []
                    for proj in task_sheet.project_ids:
                        for loc in proj.location_ids:
                            for equip in loc.equipment_ids:
                                if equip not in equip_list:
                                    equip_list.append(equip)
                    for equipment in task_sheet.equipment_ids if task_sheet.equipment_ids else equip_list:
                        task_sheet.technical_status_ids.create({
                            'equipment_id': equipment._origin.id,
                            'name': equipment.name + ' technical status' + " for " + task_sheet.name,
                            'task_sheet_id': task_sheet.id,
                        })


class MaintenanceTaskSheetLine(models.Model):
    _name = "maintenance.task.sheet.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Maintenance Task Sheet Line"

    name = fields.Char(string="Name", required=True)
    task_sheet_id = fields.Many2one(comodel_name="maintenance.task.sheet", string="Task Sheet")
    request_id = fields.Many2one(comodel_name='maintenance.request', string="Maintenance Request")

    task_line_id = fields.Many2one(comodel_name="maintenance.task.line", string="Task Line")
    project_id = fields.Many2one(comodel_name="maintenance.project", related='task_line_id.project_id')
    location_id = fields.Many2one(comodel_name="stock.location", related='task_line_id.location_id')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", related='task_line_id.equipment_id')
    task_categ_id = fields.Many2one(comodel_name="maintenance.task.categ", related='task_id.task_categ_id')
    task_id = fields.Many2one(comodel_name="maintenance.task", related='task_line_id.task_id')

    date = fields.Date(string='Date', default=fields.Date.today())
    state = fields.Selection(string="State", selection=[('yes', 'Yes'), ('no', 'No')])
    readings = fields.Char(string="Readings")
    note = fields.Text(string="Note")


class MaintenanceTechnicalStatus(models.Model):
    _name = "maintenance.technical.status"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Maintenance Technical Status"

    name = fields.Char(string="Name", help="task sheet name + date")
    task_sheet_id = fields.Many2one(comodel_name="maintenance.task.sheet", string="Task Sheet")
    equipment_id = fields.Many2one(comodel_name='maintenance.equipment', string="Equipment")
    date_state = fields.Date(string="Last Maintenance State Date", default=fields.Date.today())
    last_technical_state = fields.Text(string="Last Technical State")
    state_after_maintenance = fields.Text(string="State After Maintenance")
    repeated_errors = fields.Text(string="Frequent Faults")
