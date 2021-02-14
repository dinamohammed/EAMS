from odoo.exceptions import AccessDenied

from odoo import api, models, fields, registry, SUPERUSER_ID


class Users(models.Model):
    _inherit = "res.users"

    internal_requisition_ids = fields.Many2many('material.internal.requisition', 'material_internal_requisition_rel', string='Material Internal Requisition')