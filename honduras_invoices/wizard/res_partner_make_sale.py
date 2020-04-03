# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResPartnerMakeSale(models.TransientModel):
    _name = "res.partner.make.sale"
    _description = "Make a sale for a partner"

    order_line_ids = fields.Many2many("sale.order.line", string="Order Lines", ondelete="cascade")

    def make_sale(self):
        partner_ids = self.env["res.partner"].browse(self.env.context.get("active_ids", []))
        pass