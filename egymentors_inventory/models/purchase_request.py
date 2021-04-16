# -*- coding: utf-8 -*-

from odoo import api, fields, models

_STATES = [('draft', 'draft'),
           ('audit', 'Audit Approval'),
           ('manager', 'Manager Approval'),
           ('g_manager', 'General Manager Approval'),
           ('done', 'Done'),
           ('locked', 'Locked'),
           ('cancel', 'Cancelled')]

READONLY_STATES = {
    'draft': [('readonly', False)],
}


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Purchase Request"

    name = fields.Char("Request Reference", required=True, readonly=1, index=True, copy=False, default='New')
    date_request = fields.Datetime('Request Date', required=True, states=READONLY_STATES, index=True, copy=False,
                                   default=fields.Datetime.now, readonly=1,
                                   help="Depicts the date where the Quotation should be validated and"
                                        " converted into a purchase order.")
    req_dep_id = fields.Many2one('purchase.request.department', "Requested Department",
                                 states=READONLY_STATES, readonly=1)
    date_approve = fields.Datetime('Confirmation Date', readonly=1, index=True, copy=False)
    purchase_order_id = fields.Many2one('purchase.order', "Purchase Order", readonly=1)
    requisition_id = fields.Many2one('purchase.requisition', 'Purchase Agreement', readonly=1)

    user_id = fields.Many2one('res.users', string='Purchase Representative', index=True, tracking=True,
                              default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES,
                                 default=lambda self: self.env.company.id)
    state = fields.Selection(_STATES, string='Status', readonly=True, index=True, copy=False, default='draft',
                             tracking=True)
    request_line = fields.One2many('purchase.request.line', 'request_id', string='Request Lines', readonly=1,
                                   states=READONLY_STATES, copy=True)
    notes = fields.Text("Note", placeholder="Write Notes")
    responsible_ids = fields.Many2many(comodel_name='res.users', string="Responsible")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_request' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_request']))
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request', sequence_date=seq_date) or '/'
        return super(PurchaseRequest, self).create(vals)

    def write(self, vals):
        super(PurchaseRequest, self).write(vals)
        for request in self:
            if vals.get('state'):
                for line in request.request_line.filtered(lambda l: l.state != 'locked'):
                    line.write({'state': vals.get('state')})
        return True

    def print_request(self):
        return self.env.ref('egymentors_inventory.purchase_request_report').report_action(self)

    def button_audit_approval(self):
        self.write({'state': 'audit'})

    def button_manager_approval(self):
        self.write({'state': 'manager',
                    'date_approve': fields.Datetime.now()})

    def button_general_manager_approval(self):
        self.write({'state': 'g_manager',
                    'date_approve': fields.Datetime.now()})

    def button_done(self):
        self.write({'state': 'done'})

    def button_draft(self):
        self.write({'state': 'draft'})
        return {}

    def button_cancel(self):
        self.write({'state': 'cancel'})


class PurchaseRequestDepartment(models.Model):
    _name = 'purchase.request.department'
    _description = 'Purchase Request Department'

    name = fields.Char("Department", required=1)


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Purchase Request Line'
    _order = 'request_id, sequence, id'
    _rec_name = 'product_id'

    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=1,
                                 domain=[('purchase_ok', '=', True)], change_default=True)
    request_id = fields.Many2one('purchase.request', string='Request Reference', index=True,
                                 required=True, ondelete='cascade')
    state = fields.Selection(_STATES, string='Status', readonly=True, index=True, copy=False, default='draft',
                             tracking=True)
    note = fields.Text("Purchase Cause")
    company_id = fields.Many2one('res.company', "Company")
    req_dep_id = fields.Many2one('purchase.request.department', "Requested Department")
    date_request = fields.Datetime('Request Date', required=True, states=READONLY_STATES, index=True, copy=False,
                                   default=fields.Datetime.now, readonly=1,
                                   help="Depicts the date where the Quotation should be validated and"
                                        " converted into a purchase order.")
    reason = fields.Text(string="Rejection Reason")
    item_value = fields.Text(string="Item Value")
    item_type = fields.Text(string="Item Type")
