# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ref_2 = fields.Char(string='Reference 2')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ref_2 = fields.Char(string='Reference 2')
