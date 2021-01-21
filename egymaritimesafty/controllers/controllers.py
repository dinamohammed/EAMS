# -*- coding: utf-8 -*-
# from odoo import http


# class Egymaritimesafty(http.Controller):
#     @http.route('/egymaritimesafty/egymaritimesafty/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/egymaritimesafty/egymaritimesafty/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('egymaritimesafty.listing', {
#             'root': '/egymaritimesafty/egymaritimesafty',
#             'objects': http.request.env['egymaritimesafty.egymaritimesafty'].search([]),
#         })

#     @http.route('/egymaritimesafty/egymaritimesafty/objects/<model("egymaritimesafty.egymaritimesafty"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('egymaritimesafty.object', {
#             'object': obj
#         })
