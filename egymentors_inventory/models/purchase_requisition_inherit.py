# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning

_STATES = [('draft', 'draft'),
           ('first', 'Technical Approve'),
           ('done', 'Done'),
           ('locked', 'Locked'),
           ('cancel', 'Cancelled')]


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    @api.onchange('request_ids', 'request_id', 'multi_requisition')
    def get_request_state(self):
        for order in self:
            if order.multi_requisition and order.request_ids:
                order.request_state = order.request_ids[-1].state
            elif order.request_id:
                order.request_state = order.request_id.state
            else:
                order.request_state = 'draft'

    @api.onchange('tender_request_ids', 'tender_request_id', 'tender_multi_requisition')
    def get_tender_request_state(self):
        for order in self:
            if order.tender_multi_requisition and order.tender_request_ids:
                order.tender_request_state = order.tender_request_ids[-1].state
            elif order.tender_request_id:
                order.tender_request_state = order.tender_request_id.state
            else:
                order.tender_request_state = 'draft'

    request_added = fields.Boolean()
    multi_requisition = fields.Boolean("Multi Requests")
    request_id = fields.Many2one('purchase.request', 'Purchase Request', copy=False,
                                 domain=lambda self: "[('state', 'in', ['done'])]",
                                 help="Choose Confirmed request and load it's lines on PO")
    request_ids = fields.Many2many(comodel_name='purchase.request', copy=False,
                                   domain=lambda self: "[('state', 'in', ['done'])]")
    request_state = fields.Selection(_STATES, compute='get_request_state', required=False)

    # Tender:
    tender_request_added = fields.Boolean()
    tender_multi_requisition = fields.Boolean("Tender Multi Requests")
    tender_request_id = fields.Many2one('tender.request', 'Tender Request', copy=False,
                                        domain=lambda self: "[('state', 'in', ['done'])]",
                                        help="Choose Confirmed request and load it's lines on PO")
    tender_request_ids = fields.Many2many(comodel_name='tender.request', copy=False,
                                          domain=lambda self: "[('state', 'in', ['done'])]")
    tender_request_state = fields.Selection(_STATES, compute='get_request_state', required=False)

    signatures_ids = fields.Many2many(comodel_name='agreement.signature',
                                      help="Add signatures to be added in printouts")
    signatures_technical_ids = fields.Many2many(comodel_name='agreement.signature.technical',
                                                help="Add signatures to be added in printouts")

    @api.onchange('request_id')
    def assign_request(self):
        for req in self:
            if req.request_id:
                req.origin = req.request_id.name

    @api.onchange('tender_request_id')
    def assign_tender_request(self):
        for req in self:
            if req.tender_request_id:
                req.origin = req.tender_request_id.name

    def write(self, vals):
        if vals.get('request_id'):
            vals['origin'] = self.env['purchase.request'].browse(vals.get('request_id')).name
        if vals.get('tender_request_id'):
            vals['origin'] = self.env['tender.request'].browse(vals.get('tender_request_id')).name
        return super(PurchaseRequisitionInherit, self).write(vals)

    def load_pr_lines(self):
        for rec in self:
            if rec.multi_requisition:
                request_ids = rec.request_ids
            else:
                request_ids = [rec.request_id]
            if request_ids:
                request_products = rec.line_ids.mapped('product_id.id')
                for request_id in request_ids:
                    # if request_id.requisition_id:
                    # 	raise Warning(_("This Request %s Used Before in requisition %s") % (request_id.name,
                    # 																		rec.name))
                    for line in request_id.request_line.filtered(lambda l: l.state == 'done'):
                        if line.product_id.id in request_products:
                            p_requisition_lines = rec.line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)
                            # request_line_ids = p_requisition_lines[0].request_line_ids.ids
                            # request_line_ids.append(line.id)
                            p_requisition_lines[0].write(
                                {'product_qty': line.product_qty + p_requisition_lines[0].product_qty,
                                 'request_line_ids': [(6, 0, [line.id])]})
                        else:
                            rec.line_ids.create({
                                'requisition_id': rec.id,
                                'product_id': line.product_id.id,
                                'request_line_ids': [(6, 0, [line.id])],
                                'product_qty': line.product_qty,
                                'price_unit': 0.0,
                                'product_uom_id': line.product_id.uom_po_id and line.product_id.uom_po_id.id or line.product_id.uom_id.id,
                            })
                            request_products.append(line.product_id.id)
                    # 'state': 'locked',
                    request_id.write({'requisition_id': rec.id})
                rec.request_added = True
            else:
                raise Warning(_("No Request To load"))

    def load_tr_lines(self):
        for rec in self:
            if rec.tender_multi_requisition:
                tender_request_ids = rec.tender_request_ids
            else:
                tender_request_ids = [rec.tender_request_id]
            if tender_request_ids:
                tender_request_products = rec.line_ids.mapped('product_id.id')
                for tender_request_id in tender_request_ids:
                    # if request_id.requisition_id:
                    # 	raise Warning(_("This Request %s Used Before in requisition %s") % (request_id.name,
                    # 																		rec.name))
                    for line in tender_request_id.tender_request_line.filtered(lambda l: l.state == 'done'):
                        if line.product_id.id in tender_request_products:
                            p_requisition_lines = rec.line_ids.filtered(lambda l: l.product_id.id == line.product_id.id)
                            # tender_request_line_ids = p_requisition_lines[0].request_line_ids.ids
                            # tender_request_line_ids.append(line.id)
                            p_requisition_lines[0].write(
                                {'product_qty': line.product_qty + p_requisition_lines[0].product_qty,
                                 'tender_request_line_ids': [(6, 0, [line.id])]})
                        else:
                            rec.line_ids.create({
                                'requisition_id': rec.id,
                                'product_id': line.product_id.id,
                                'tender_request_line_ids': [(6, 0, [line.id])],
                                'product_qty': line.product_qty,
                                'price_unit': 0.0,
                                'product_uom_id': line.product_id.uom_po_id and line.product_id.uom_po_id.id or line.product_id.uom_id.id,
                            })
                            tender_request_products.append(line.product_id.id)
                    # 'state': 'locked',
                    tender_request_id.write({'requisition_id': rec.id})
                rec.tender_request_added = True
            else:
                raise Warning(_("No Request To load"))

    def remove_pr_lines(self):
        for requisition_id in self:
            if requisition_id.multi_requisition:
                request_ids = requisition_id.request_ids
            else:
                request_ids = [requisition_id.request_id]
            if request_ids:
                for request_id in request_ids:
                    for line in request_id.request_line:
                        request_line = requisition_id.line_ids.filtered(lambda l: line.id in l.request_line_ids.ids)
                        if request_line:
                            # IT's Only Line Created with pr Line qty
                            if request_line[0].product_qty == line.product_qty:
                                request_line[0].unlink()
                            # IT's Order Line And will deduct pr line qty
                            elif request_line[0].product_qty > line.product_qty:
                                request_line_list = request_line[0].request_line_ids.ids
                                request_line_ids = False
                                if request_line_list:
                                    if len(request_line_list) > 1:
                                        request_line_list.remove(line.id)
                                        request_line_ids = [(6, 0, request_line_list)]
                                request_line[0].write({'product_qty': request_line.product_qty - line.product_qty,
                                                       'request_line_ids': request_line_ids})
                            # THis line is edit and qty is bellow pr line qty (User miss using)
                            else:
                                raise Warning(_("User Changed Qty for this product [%s]\n"
                                                " Please Make it's qty bigger than Requisition request line qty:%s") % (
                                                  request_line[0].product_id.display_name, line.product_qty
                                              ))
                    request_id.write({'state': 'done', 'requisition_id': False})
                requisition_id.request_added = False
            else:
                raise Warning(_("No Request To remove"))

    def remove_tr_lines(self):
        for tender_requisition_id in self:
            if tender_requisition_id.tender_multi_requisition:
                tender_request_ids = tender_requisition_id.tender_request_ids
            else:
                tender_request_ids = [tender_requisition_id.tender_request_id]
            if tender_request_ids:
                for tender_request_id in tender_request_ids:
                    for line in tender_request_id.tender_request_line:
                        tender_request_line = tender_requisition_id.line_ids.filtered(
                            lambda l: line.id in l.tender_request_line_ids.ids)
                        if tender_request_line:
                            # IT's Only Line Created with tr Line qty
                            if tender_request_line[0].product_qty == line.product_qty:
                                tender_request_line[0].unlink()
                            # IT's Order Line And will deduct tr line qty
                            elif tender_request_line[0].product_qty > line.product_qty:
                                tender_request_line_list = tender_request_line[0].tender_request_line_ids.ids
                                tender_request_line_ids = False
                                if tender_request_line_list:
                                    if len(tender_request_line_list) > 1:
                                        tender_request_line_list.remove(line.id)
                                        tender_request_line_ids = [(6, 0, tender_request_line_list)]
                                tender_request_line[0].write(
                                    {'product_qty': tender_request_line.product_qty - line.product_qty,
                                     'tender_request_line_ids': tender_request_line_ids})
                            # THis line is edit and qty is bellow tr line qty (User miss using)
                            else:
                                raise Warning(_("User Changed Qty for this product [%s]\n"
                                                " Please Make it's qty bigger than Requisition request line qty:%s") % (
                                                  tender_request_line[0].product_id.display_name, line.product_qty
                                              ))
                    tender_request_id.write({'state': 'done', 'requisition_id': False})
                tender_requisition_id.tender_request_added = False
            else:
                raise Warning(_("No Request To remove"))


class PurchaseRequisitionLineInherit(models.Model):
    _inherit = 'purchase.requisition.line'

    request_line_ids = fields.Many2many('purchase.request.line', string="Request Line")
    tender_request_line_ids = fields.Many2many('tender.request.line', string="Tender Request Line")

    def _prepare_purchase_order_line(self, name, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        res = super(PurchaseRequisitionLineInherit, self)._prepare_purchase_order_line(name, product_qty, price_unit,
                                                                                       taxes_ids)
        if self.request_line_ids:
            res['request_line_ids'] = [(6, 0, self.request_line_ids.ids)]
        if self.tender_request_line_ids:
            res['tender_request_line_ids'] = [(6, 0, self.tender_request_line_ids.ids)]
        res['requisition_line_id'] = self.id
        return res
