# -*- coding: utf-8 -*-
# from odoo import http


# class MultipleDiscount(http.Controller):
#     @http.route('/multiple_discount/multiple_discount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multiple_discount/multiple_discount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('multiple_discount.listing', {
#             'root': '/multiple_discount/multiple_discount',
#             'objects': http.request.env['multiple_discount.multiple_discount'].search([]),
#         })

#     @http.route('/multiple_discount/multiple_discount/objects/<model("multiple_discount.multiple_discount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multiple_discount.object', {
#             'object': obj
#         })
