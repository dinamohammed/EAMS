# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class AccountCheckActionWizard(models.TransientModel):
    _name = 'account.check.action.wizard'
    _description = 'Account Check Action Wizard'

    date = fields.Date(
        default=fields.Date.context_today,
        required=True,
    )
    action_type = fields.Char(
        'Action type passed on the context',
        required=True,
    )

    def action_confirm(self):
        self.ensure_one()
        if self.action_type not in ['claim', 'bank_debit', 'reject']:
            raise ValidationError(_(
                'Action %s not supported on checks') % self.action_type)
        check = self.env['account.check'].browse(
            self._context.get('active_id'))
        if self.action_type == 'bank_debit' and self.date and \
                check.payment_date and self.date < check.payment_date:
            raise Warning("Check Debited date cannot be before payment date: %s" % self.check_id.payment_date)
        return getattr(
            check.with_context(action_date=self.date), self.action_type)()
