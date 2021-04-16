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


class TenderRequest(models.Model):
    _name = 'tender.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Tender Request"

    # def _tender_responsible_domain(self):
    #     users = self.env['res.users'].search([])
    #     domain = [('id' 'in', [usr.id for usr in users if usr.user_has_groups('purchase.group_purchase_user')])]
    #     return domain

    name = fields.Char(string="Request Reference", required=True, readonly=1, index=True, copy=False, default='New')
    date_request = fields.Datetime(string='Request Date', required=True, states=READONLY_STATES, index=True, copy=False,
                                   default=fields.Datetime.now, readonly=1,
                                   help="Depicts the date where the Quotation should be validated and"
                                        " converted into a tender order.")
    req_dep_id = fields.Many2one(comodel_name='tender.request.department', string="Requested Department",
                                 states=READONLY_STATES, readonly=1)
    date_approve = fields.Datetime(string='Confirmation Date', readonly=1, index=True, copy=False)
    tender_order_id = fields.Many2one(comodel_name='tender.order', string="Tender Order", readonly=1)
    requisition_id = fields.Many2one(comodel_name='purchase.requisition', string='Tender Agreement', readonly=1)
    user_id = fields.Many2one(comodel_name='res.users', string='Tender Representative', index=True, tracking=True,
                              default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', required=True, index=True,
                                 states=READONLY_STATES, default=lambda self: self.env.company.id)
    state = fields.Selection(_STATES, string='Status', readonly=True, index=True, copy=False, default='draft',
                             tracking=True)
    tender_request_line = fields.One2many(comodel_name='tender.request.line', inverse_name='tender_request_id',
                                          string='Request Lines', readonly=1, states=READONLY_STATES, copy=True)
    notes = fields.Text("Notes", placeholder="Write Notes")
    tender_responsible_ids = fields.Many2many(comodel_name='res.users', string="Responsible")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_request' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_request']))
            vals['name'] = self.env['ir.sequence'].next_by_code('tender.request', sequence_date=seq_date) or '/'
        return super(TenderRequest, self).create(vals)

    def write(self, vals):
        super(TenderRequest, self).write(vals)
        for request in self:
            if vals.get('state'):
                for line in request.tender_request_line.filtered(lambda l: l.state != 'locked'):
                    line.write({'state': vals.get('state')})
        return True

    def print_request(self):
        return self.env.ref('egymentors_inventory.purchase_request_report').report_action(self)

    def button_audit_approval(self):
        # for request in self:
        # 	if not request.tender_request_line:
        # 		raise Warning(_("You should add line at least to approve request!!!"))
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


class TenderRequestDepartment(models.Model):
    _name = 'tender.request.department'
    _description = 'Tender Request Department'

    name = fields.Char(string="Department", required=1)


class TenderRequestLine(models.Model):
    _name = 'tender.request.line'
    _description = 'Tender Request Line'
    _order = 'tender_request_id, sequence, id'
    _rec_name = 'product_id'

    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=1,
                                 domain=[('purchase_ok', '=', True)], change_default=True)
    tender_request_id = fields.Many2one(comodel_name='tender.request', string='Request Reference', index=True, required=True,
                                 ondelete='cascade')
    state = fields.Selection(_STATES, string='Status', readonly=True, index=True, copy=False, default='draft',
                             tracking=True)
    note = fields.Text(string="Tender reason")
    company_id = fields.Many2one(comodel_name='res.company', string="Company")
    req_dep_id = fields.Many2one(comodel_name='tender.request.department', string="Requested Department")
    date_request = fields.Datetime(string='Request Date', required=True, states=READONLY_STATES, index=True, copy=False,
                                   default=fields.Datetime.now, readonly=1,
                                   help="Depicts the date where the Quotation should be validated and"
                                        " converted into a tender order.")
    reason = fields.Text(string="Rejection Reason")
    item_value = fields.Text(string="Item Value")
    item_type = fields.Text(string="Item type")
