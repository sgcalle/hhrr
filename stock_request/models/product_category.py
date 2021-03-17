#-*- coding:utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"

    stock_request_cost_method = fields.Selection(string="Stock Request Costing Method",
        selection=[
            ("product_cost", "Cost defined in product"),
            ("upon_request", "Upon Request"),
            ("upon_transfer_creation", "Upon Transfer Creation"),
            ("upon_delivery", "Upon Delivery")],
        required=True,
        default="product_cost")
    stock_request_cost_from_valuation = fields.Boolean(string="Get Cost from Valuations",
        help="If checked, cost of storable type products under this category will be computed "
            "from the valuations generated after validating the transfer")
    stock_request_cost_basis = fields.Selection(string="Stock Request Cost Basis",
        selection=[
            ("requested", "Requested"),
            ("delivered", "Delivered")],
        required=True,
        default="delivered")