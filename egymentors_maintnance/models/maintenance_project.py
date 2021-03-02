# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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

    name = fields.Char(string="Name", required=False)
    project_id = fields.Many2one(comodel_name="maintenance.project", related='equipment_id.project_id')
    location_id = fields.Many2one(comodel_name="stock.location", related='equipment_id.location_id')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipment")
    task_categ_id = fields.Many2one(comodel_name="maintenance.task.categ", string="Task Category", required=True)
    task_id = fields.Many2one(comodel_name="maintenance.task", string="Maintenance Task", required=True)
    date = fields.Date(default=fields.Date.today(), string='Date')
    state = fields.Selection(string="State", selection=[('yes', 'Yes'), ('no', 'No')])
    note = fields.Text()

    @api.onchange('task_categ_id')
    def onchange_task_categ_id(self):
        for task in self:
            task.task_id = False
            return {'domain': {
                'task_id': [('task_categ_id', '=', task.task_categ_id.id)]
            }}


class MaintenanceTaskCategory(models.Model):
    _name = "maintenance.task.categ"
    _description = "Task Category"

    name = fields.Char(string="Name")
    task_ids = fields.One2many(comodel_name="maintenance.task", inverse_name="task_categ_id", string="Tasks")


class MaintenanceTask(models.Model):
    _name = "maintenance.task"
    _description = "Maintenance Task"

    name = fields.Char()
    task_categ_id = fields.Many2one(comodel_name="maintenance.task.categ", string="Task Category", required=True)


class MaintenanceTaskSheet(models.Model):
    _name = "maintenance.task.sheet"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Maintenance Task Sheet"

    name = fields.Char(string="Name", required=True)
    project_ids = fields.Many2many(comodel_name="maintenance.project", string="Project", required=True)
    location_ids = fields.Many2many(comodel_name="stock.location", string="Location")
    equipment_ids = fields.Many2many(comodel_name="maintenance.equipment", string="Equipment")
    task_categ_ids = fields.Many2many(comodel_name="maintenance.task.categ", string="Task Category")
    task_sheet_line_ids = fields.One2many(comodel_name="maintenance.task.sheet.line", inverse_name="task_sheet_id",
                                          string="Task Sheet Line")

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
        task_line_obj = self.env['maintenance.task.line']
        for task in self:
            task.task_categ_ids = False
            # categ_ids = self.env['maintenance.task.categ'].search([('id', 'in', task.task_categ_ids.ids)])
            # equipment_ids = self.env['maintenance.equipment'].search('task_ids')
            # categ_ids = task.equipment_ids.task_ids.mapped('task_categ_id')
            task_lines = task_line_obj.search([('equipment_id', 'in', task.equipment_ids.ids)])
            return {'domain': {
                'task_categ_ids': [('id', 'in', task_lines.mapped('task_categ_id').ids)],
            }}

    @api.onchange('project_ids', 'location_ids', 'equipment_ids', 'task_categ_ids')
    def compute_task_sheet_lines_domain(self):
        domain = []
        for task_sheet in self:
            if task_sheet.project_ids:
                if task_sheet.project_ids or task_sheet.location_ids or task_sheet.equipment_ids or task_sheet.task_categ_ids:
                    if not task_sheet.name:
                        raise ValidationError(_("Please define Task sheet name."))
                    if task_sheet.project_ids:
                        domain.append(('project_id', 'in', task_sheet.project_ids.ids))
                    if task_sheet.location_ids:
                        if len(domain) > 0:
                            domain = ['|'] + domain
                            domain.append(('location_id', 'in', task_sheet.location_ids.ids))
                        else:
                            domain.append(('location_id', 'in', task_sheet.location_ids.ids))
                    if task_sheet.equipment_ids:
                        if len(domain) > 0:
                            domain = ['|'] + domain
                            domain.append(('equipment_id', 'in', task_sheet.equipment_ids.ids))
                        else:
                            domain.append(('equipment_id', 'in', task_sheet.equipment_ids.ids))
                    if task_sheet.task_categ_ids:
                        if len(domain) > 0:
                            domain = ['|'] + domain
                            domain.append(('task_categ_id', 'in', task_sheet.task_categ_ids.ids))
                        else:
                            domain.append(('task_categ_id', 'in', task_sheet.task_categ_ids.ids))

                    task_lines = self.env['maintenance.task.line'].search(domain)

                    task_sheet.task_sheet_line_ids = False

                    for task_line in task_lines:
                        task_sheet.task_sheet_line_ids.create({
                            'name': task_sheet.name,
                            'task_sheet_id': task_sheet.id,
                            'task_line_id': task_line.id,
                        })
                    # task.task_sheet_line_ids = [(6, 0, task_line_ids)]

                    # task.write({'task_sheet_line_ids': [(6, 0, task_lines.mapped('id'))]})
                    # cls.journal.edi_format_ids = [(6, 0, cls.edi_format.ids)]
                    # task.task_sheet_line_ids.write({
                    # })
                    # x = task_sheet.task_sheet_line_ids


class MaintenanceTaskSheetLine(models.Model):
    _name = "maintenance.task.sheet.line"
    _description = "Maintenance Task Sheet Line"

    name = fields.Char(string="Name", required=False)
    task_sheet_id = fields.Many2one(comodel_name="maintenance.task.sheet", string="Task Sheet")

    task_line_id = fields.Many2one(comodel_name="maintenance.task.line", string="Task Line")
    project_id = fields.Many2one(comodel_name="maintenance.project", related='task_line_id.project_id')
    location_id = fields.Many2one(comodel_name="stock.location", related='task_line_id.location_id')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", related='task_line_id.equipment_id')
    task_id = fields.Many2one(comodel_name="maintenance.task", related='task_line_id.task_id')
    task_categ_id = fields.Many2one(comodel_name="maintenance.task.categ", related='task_id.task_categ_id')

    date = fields.Date(string='Date', default=fields.Date.today())
    state = fields.Selection(string="State", selection=[('yes', 'Yes'), ('no', 'No')])
    note = fields.Text(string="Note")
