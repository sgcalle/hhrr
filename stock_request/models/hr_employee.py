#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    stock_request_portal_access = fields.Boolean(string="Stock Request Portal Access",
        groups="hr.group_hr_user")