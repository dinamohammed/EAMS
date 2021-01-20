# -*- coding: utf-8 -*-
# from odoo import http


# class CustomePayslip(http.Controller):
#     @http.route('/custome_payslip/custome_payslip/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custome_payslip/custome_payslip/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custome_payslip.listing', {
#             'root': '/custome_payslip/custome_payslip',
#             'objects': http.request.env['custome_payslip.custome_payslip'].search([]),
#         })

#     @http.route('/custome_payslip/custome_payslip/objects/<model("custome_payslip.custome_payslip"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custome_payslip.object', {
#             'object': obj
#         })
