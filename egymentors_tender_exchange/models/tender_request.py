from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


# from datetime import datetime, date
# import odoo.addons.decimal_precision as dp


class TenderRequest(models.Model):
    _name = 'tender.request'
    _description = 'Tender Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'id desc'

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _default_company(self):
        return self.env.user.company_id.id

    name = fields.Char(string='Number', index=True, readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee, required=True, copy=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True, copy=True)
    company_id = fields.Many2one('res.company', string='Company', default=_default_company, required=True, copy=True)
    tender_responsible_id = fields.Many2one('hr.employee', string='Requisition Responsible', copy=True)

    date_request = fields.Date(string='Request Date', default=fields.Date.today(), required=True)
    date_receive = fields.Date(string='Received Date', readonly=True, copy=False)
    date_end = fields.Date(string='Tender Deadline', readonly=True, help='Last date for the product to be needed',
                           copy=True)

    tender_line_ids = fields.One2many('tender.request.line', 'tender_id',
                                      string='Internal Requisitions Line', copy=True)

    location_id = fields.Many2one('stock.location', string='Source Location', copy=True)
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', required=False, copy=True,
                                       help="Location where the system will stock the finished products.")
    delivery_picking_id = fields.Many2one('stock.picking', string='Internal Picking', readonly=True, copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', copy=False)
    internal_picking_count = fields.Integer('Internal Picking', compute='_get_internal_picking_count')

    employee_confirm_id = fields.Many2one('hr.employee', string='Confirmed By', readonly=True, copy=False)
    approve_employee_id = fields.Many2one('hr.employee', string='Approved By', readonly=True, copy=False)
    approve_manager_id = fields.Many2one('hr.employee', string='Department Manager', readonly=True, copy=False)
    reject_employee_id = fields.Many2one('hr.employee', string='Rejected By', readonly=True, copy=False)
    reject_manager_id = fields.Many2one('hr.employee', string='Department Manager Reject', readonly=True, copy=False)

    date_confirm = fields.Date(string='Confirmed Date', readonly=True, copy=False)
    date_manager_approved = fields.Date(string='Department Approval Date', readonly=True, copy=False)
    date_user_approved = fields.Date(string='Approved Date', readonly=True, copy=False)
    date_user_reject = fields.Date(string='Rejected Date', readonly=True, copy=False)

    date_done = fields.Date(string='Date Done', readonly=True, help='Date of Completion of Internal Requisition')

    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approved'),
        ('approve', 'Approved'),
        ('stock', 'Requested'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        track_visibility='onchange'
    )
    note = fields.Text(string='Reason for Tender', required=False, copy=True)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for rec in self:
            rec.department_id = rec.employee_id.sudo().department_id.id
            rec.dest_location_id = rec.employee_id.sudo().dest_location_id.id or rec.employee_id.sudo().department_id.dest_location_id.id

    @api.onchange('date_end')
    def onchange_date_end(self):
        res = {}
        if not self.date_end:
            return res
        else:
            if self.date_end < fields.Date.today():
                res = self.date_end = False
                return res

    def _get_internal_picking_count(self):
        for tender in self:
            tender.internal_picking_count = self.env['stock.picking'].sudo().search_count(
                [('tender_id', '=', tender.id)])

    def action_view_stock_picking(self):
        self.ensure_one()
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('tender_id', '=', self.id)]
        return action

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise ValidationError(_(
                    'You cannot delete an tender request unless the status of the request is new, canceled, or rejected.'))
        return super(TenderRequest, self).unlink()

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('tender.request.sequence')
        vals.update({
            'name': name
        })
        res = super(TenderRequest, self).create(vals)
        res_users_obj = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        if res_users_obj:
            res_users_obj.sudo().write({'tender_request_ids': [(4, res.id)]})
        return res

    def tender_confirm(self):
        for rec in self:
            email_template_to_department_manager = self.env.ref(
                'egymentors_tender_exchange.email_template_tender_to_department_manager')
            rec.employee_confirm_id = rec.employee_id.id
            rec.date_confirm = fields.Date.today()
            rec.state = 'dept_confirm'
            if email_template_to_department_manager:
                email_template_to_department_manager.send_mail(self.id)

    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.date_user_reject = fields.Date.today()

    def manager_approve(self):
        for rec in self:
            rec.date_manager_approved = fields.Date.today()
            rec.approve_manager_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

            email_template_to_manager = self.env.ref('egymentors_tender_exchange.email_template_tender_to_manager')
            email_template_to_employee = self.env.ref('egymentors_tender_exchange.email_template_tender_to_employee')

            if email_template_to_employee:
                email_template_to_employee.send_mail(rec.id)
            if email_template_to_manager:
                email_template_to_manager.send_mail(rec.id)

            rec.state = 'ir_approve'

    def user_approve(self):
        for rec in self:
            rec.date_user_approved = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_received(self):
        for rec in self:
            rec.date_receive = fields.Date.today()
            rec.state = 'receive'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        for rec in self:
            if not rec.requisition_line_ids:
                raise ValidationError(_('Please create some tender lines.'))

            if any(line.tender_type == 'internal' for line in rec.tender_line_ids):
                if not rec.location_id.id:
                    raise ValidationError(_('Select Source location under the picking details.'))
                if not rec.picking_type_id.id:
                    raise ValidationError(_('Select Picking Type under the picking details.'))
                if not rec.dest_location_id:
                    raise ValidationError(_('Select Destination location under the picking details.'))

                stock_id = stock_obj.sudo().create({
                    'partner_id': rec.employee_id.sudo().user_id.partner_id.id or False,
                    'location_id': rec.location_id.id,
                    'location_dest_id': rec.dest_location_id and rec.dest_location_id.id or rec.employee_id.dest_location_id.id or rec.employee_id.department_id.dest_location_id.id,
                    'picking_type_id': rec.picking_type_id.id,
                    'note': rec.note,
                    'tender_id': rec.id,
                    'origin': rec.name,
                })
                rec.write({
                    'delivery_picking_id': stock_id.id,
                })

            for line in rec.tender_line_ids:
                if line.tender_type == 'internal':
                    move_id = move_obj.sudo().create({
                        'picking_type_id': self.picking_type_id.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_uom_qty': line.qty,
                        'product_uom': line.uom.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.dest_location_id.id,
                        'picking_id': stock_id.id,
                        'tender_request_line_id': line.id
                    })
                    line.stock_move_id = move_id
                rec.state = 'stock'


class TenderRequestLine(models.Model):
    _name = "tender.request.line"

    tender_id = fields.Many2one('tender.request', string='Tender', )
    product_id = fields.Many2one('product.product', string='Product', required=True, )
    description = fields.Char(string='Description', required=True, )
    qty = fields.Float(string='Quantity', default=1, required=True, )
    uom = fields.Many2one('uom.uom', string='Unit of Measure', required=True, )
    partner_id = fields.Many2many('res.partner', string='Vendors', )
    tender_type = fields.Selection(selection=[
        ('internal', 'Internal Picking'),
    ], string='Requisition Action', default='internal', required=True, )
    virtual_available = fields.Float(related='product_id.virtual_available', string='Forecasted')
    qty_available = fields.Float(related='product_id.qty_available', string='On Hand')
    stock_move_id = fields.Many2one(comodel_name='stock.move', string="Move")
    product_uom_qty = fields.Float(related='stock_move_id.product_uom_qty')
    quantity_done = fields.Float(related='stock_move_id.quantity_done')

    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.description = rec.product_id.name
            rec.uom = rec.product_id.uom_id.id
