# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentRegister(http.Controller):
#     @http.route('/payment_register/payment_register/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_register/payment_register/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_register.listing', {
#             'root': '/payment_register/payment_register',
#             'objects': http.request.env['payment_register.payment_register'].search([]),
#         })

#     @http.route('/payment_register/payment_register/objects/<model("payment_register.payment_register"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_register.object', {
#             'object': obj
#         })
