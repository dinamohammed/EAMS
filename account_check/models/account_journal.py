# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    checkbook_ids = fields.One2many(
        'account.checkbook',
        'journal_id',
        'Checkbooks',
    )

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
    under_collection_account_id = fields.Many2one(
        'account.account',
        'Under Collection Check Account',
        help='Holding Checks account for third checks, '
             'for eg. "Under Collection Checks"',
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
        elif check_type == 'under_collection':
            account = self.under_collection_account_id
        else:
            raise UserError(_("Type %s not implemented!"))
        if not account:
            raise UserError(_(
                'No checks of type [%s] account defined for Journal [%s]'
            ) % (check_type, self.name))
        return account
    
    @api.model
    def create(self, vals):
        rec = super(AccountJournal, self).create(vals)
        issue_checks = self.env.ref(
            'account_check.account_payment_method_issue_check')
        if (issue_checks in rec.outbound_payment_method_ids and
                not rec.checkbook_ids):
            rec._create_checkbook()
        return rec

    def _create_checkbook(self):
        """ Create a check sequence for the journal """
        checkbook = self.checkbook_ids.create({
            'journal_id': self.id,
        })
        checkbook.state = 'active'

    @api.model
    def _enable_issue_check_on_bank_journals(self):
        """ Enables issue checks payment method
            Called upon module installation via data file.
        """
        issue_checks = self.env.ref('account_check.account_payment_method_issue_check')
        domain = [('type', '=', 'bank')]
        force_company_id = self._context.get('force_company_id')
        if force_company_id:
            domain += [('company_id', '=', force_company_id)]
        bank_journals = self.search(domain)
        for bank_journal in bank_journals:
            if not bank_journal.checkbook_ids:
                bank_journal._create_checkbook()
            bank_journal.write({
                'outbound_payment_method_ids': [(4, issue_checks.id, None)],
            })
