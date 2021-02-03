# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    rejected_check_account_id = fields.Many2one(
        'account.account',
        'Rejected Check Account',
        help='Rejection Checks account, for eg. "Rejected Checks"',
        # domain=[('type', 'in', ['other'])],
    )
    deferred_check_account_id = fields.Many2one(
        'account.account',
        'Deferred Check Account',
        help='Deferred Checks account, for eg. "Deferred Checks"',
        # domain=[('type', 'in', ['other'])],
    )
    holding_check_account_id = fields.Many2one(
        'account.account',
        'Holding Check Account',
        help='Holding Checks account for third checks, '
        'for eg. "Holding Checks"',
        # domain=[('type', 'in', ['other'])],
    )

    inbank_check_account_id = fields.Many2one(
        'account.account',
        'In Bank Check Account',
        help='In Bank Checks account for Received checks, '
             'for eg. "In Bank Checks"',
        # domain=[('type', 'in', ['other'])],
    )


    def _get_check_account(self, check_type):
        self.ensure_one()
        if check_type == 'holding':
            account = self.holding_check_account_id
        elif check_type == 'rejected':
            account = self.rejected_check_account_id
        elif check_type == 'deferred':
            account = self.deferred_check_account_id
        elif check_type == 'inbank':
            account = self.inbank_check_account_id
        else:
            raise UserError(_("Type %s not implemented!"))
        if not account:
            raise UserError(_(
                'No checks %s account defined for company %s'
            ) % (check_type, self.name))
        return account
