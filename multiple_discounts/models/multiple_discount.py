# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MultipleDiscounts(models.Model):
    _name = 'multiple_discounts.discount'
    _description = 'Multiple Discounts applicable to customers'

    name = fields.Char()
    percent = fields.Float("Percent")