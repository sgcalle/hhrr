# -*- coding: utf-8 -*-

from odoo import models, fields, api


class payment_register(models.Model):
    _name = 'payment_register.payment_register'
    _description = 'payment_register.payment_register'

    name = fields.Char()

