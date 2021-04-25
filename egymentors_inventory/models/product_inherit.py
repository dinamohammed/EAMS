# -*- coding: utf-8 -*-
from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ref_2 = fields.Char(string='Reference 2')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    ref_2 = fields.Char(string='Reference 2')
    color_ids = fields.Many2many(comodel_name='product.template.attribute.value', compute='compute_color_ids',
                                 string="Color Attribute Values")
    html_color = fields.Char()

    def compute_color_ids(self):
        for variant in self:
            color_list = []
            for atr in variant.product_template_attribute_value_ids:
                if atr.attribute_id.name == "Color":
                    color_list.append(atr.id)
            variant.color_ids = [(6, 0, color_list)]
