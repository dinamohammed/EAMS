# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductProductInherit(models.Model):
    _inherit = "product.product"

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Maintenance Project Equipment")
