#-*- coding:utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    stock_request_id = fields.Many2one(string="Stock Request",
        comodel_name="stock.request",
        related="group_id.stock_request_id",
        store=True)