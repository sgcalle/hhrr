#-*- coding:utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    stock_request_ok = fields.Boolean(string="Can be Requested Internally")