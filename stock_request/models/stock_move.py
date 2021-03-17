#-*- coding:utf-8 -*-

from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = "stock.move"

    stock_request_line_id = fields.Many2one(string="Stock Request Line",
        comodel_name="stock.request.line",
        index=True)
    
    @api.constrains("state")
    def _update_stock_request_line_unit_cost(self):
        for move in self:
            if move.state == "done" and move.stock_request_line_id:
                move.stock_request_line_id.unit_cost = move.product_id.standard_price