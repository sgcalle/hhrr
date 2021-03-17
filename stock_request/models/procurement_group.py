#-*- coding:utf-8 -*-

from odoo import models, fields, api

class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    stock_request_id = fields.Many2one(string="Stock Request",
        comodel_name="stock.request")