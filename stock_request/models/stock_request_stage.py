#-*- coding:utf-8 -*-

from odoo import models, fields, api

class StockRequestStage(models.Model):
    _name = "stock.request.stage"
    _description = "Stock Request Stage"
    _order = "sequence"

    name = fields.Char(string="Name",
        required=True)
    sequence = fields.Integer(string="Sequence",
        default=100)
    dept_head_as_approver = fields.Boolean(string="Dept. Head as Approver")
    approver_ids = fields.Many2many(string="Approvers",
        comodel_name="res.users",
        relation="stock_request_stage_approver_rel")
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        default=lambda self: self.env.company)
    generate_picking = fields.Boolean(string="Generate Transfers",
        help="If checked, transfers are generated when request reaches this stage")