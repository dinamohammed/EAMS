# -*- coding: utf-8 -*-
#######################################
# Ahmed Salama
#######################################
from odoo.exceptions import Warning
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountCheckActionInbank(models.TransientModel):
    _name = 'account_check_action'
    
    @api.model
    def _get_company_id(self):
        active_ids = self._context.get('active_ids', [])
        checks = self.env['account.check'].browse(active_ids)
        company_ids = [x.company_id.id for x in checks]
        if len(set(company_ids)) > 1:
            raise Warning(_('All checks must be from the same company!'))
        return self.env['res.company'].search(
            [('id', 'in', company_ids)], limit=1)
    
    check_id = fields.Many2one('account.check', "check",
                               default=lambda x:x.env['account.check'].browse(x.env.context.get('active_id')))
    journal_id = fields.Many2one(
        'account.journal',
        'Journal',
        domain="[('company_id','=',company_id),('type', 'in', ['cash', 'bank', 'general']), ]")
    account_id = fields.Many2one(
        'account.account',
        'Account',
        domain="[('company_id','=',company_id),]")
    debited_account_id = fields.Many2one(
        'account.account',
        'Debited Account',
        domain="[('company_id','=',company_id),]")
    date = fields.Date(
        'Date', required=True, default=fields.Date.context_today
    )
    action_type = fields.Char(
        'Action type passed on the context', required=True
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        default=_get_company_id
    )
    inbank_account_id = fields.Many2one('account.account', string='In Bank Account')
    partner_id = fields.Many2one('res.partner', string='Partner')
    
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        """
        on choosing journal get his default debit account as choosen account
		return:
		"""
        self.debited_account_id = self.journal_id.default_debit_account_id.id
        
    @api.model
    def validate_inbank_action(self, action_type, check):
        """
        :param action_type:
        :param check:
        :return: move vals , check_type , inbank_account if exist
        """
        inbank_account_id = False
        check_type = False
        debit_account = credit_account = False
        if check.journal_id.currency_id and check.journal_id.currency_id != check.currency_id:
            raise Warning(_("Different currencies between check currency [%s] "
                            "and it's journal [%s] currency [%s]" % (check.currency_id and check.currency_id.name,
                                                                     check.journal_id.name,
                                                                     check.journal_id.currency_id.name)))
        if not check.journal_id.default_debit_account_id:
            raise Warning(
                _('You must selected default debit account on this check Journal.'))
        elif action_type == 'under_collection':
            if check.type == 'third_check':
                if check.state != 'handed':
                    raise Warning(
                        _('The selected checks must be in Handed state.'))
                # Filling data of move vals and lines
                check_type = "under_collection"
                debit_account = self.journal_id._get_check_account('under_collection')
                credit_account = self.journal_id._get_check_account('holding')
                name = _('Check "%s" under collection') % (check.name)
            else:  # third
                raise Warning(_('You can not debit a Isssue Check.'))
        if action_type == 'inbank':
            if check.type == 'third_check':
                if check.state not in ['handed', 'returned', 'under_collection']:
                    raise Warning(
                        _('The selected checks must be in [Handed or In Bank] state.'))
                if self.date and check.payment_date and self.date < check.payment_date:
                    raise Warning("Check Inbank date cannot be before payment date: %s" % check.payment_date)
                # Filling data of move vals and lines
                check_type = 'inbank'
                # credit_account = check.journal_id.default_debit_account_id
                if self.env.context.get('check_validation') == 'two':
                    credit_account = self.journal_id._get_check_account('holding')
                if self.env.context.get('check_validation') == 'three':
                    credit_account = self.journal_id._get_check_account('under_collection')
                debit_account = self.account_id
                name = _('Check "%s" inbank') % (check.name)
                inbank_account_id = self.account_id
            
            else:  # issue
                raise Warning(_('You can not inbank a Issue Check.'))
        elif action_type == 'bank_debit':
            if check.type == 'third_check':
                if check.state != 'inbank':
                    raise Warning(
                        _('The selected checks must be in Inbank state.'))
                # Filling data of move vals and lines
                check_type = "debited"
                # credit_account = self.journal_id.default_debit_account_id
                debit_account = self.journal_id.default_debit_account_id
                credit_account = self.inbank_account_id
                name = _('Check "%s" debit') % (check.name)
            else:  # third
                raise Warning(_('You can not debit a Isssue Check.'))
        elif action_type == 'returned':
            if check.type == 'third_check':
                if check.state not in ['handed', 'under_collection']:
                    raise Warning(_('The selected checks must be in handed/ Under collection state.'))
                # TODO implement return issue checks and return handed third checks
                check_type = "returned"
                # debit_account = self.journal_id._get_check_account('holding')
                # credit_account = self.inbank_account_id
                if self.env.context.get('check_validation') == 'two':
                    debit_account = self.partner_id.property_account_receivable_id
                    credit_account = self.journal_id._get_check_account('holding')
                if self.env.context.get('check_validation') == 'three':
                    debit_account = self.journal_id._get_check_account('holding')
                    credit_account = self.journal_id._get_check_account('under_collection')
                name = _('Check "%s" returned') % (check.name)
            else:  # issue
                raise Warning(_('You can not return a Issue Check.'))
        elif action_type == 'rejected':
            if check.type == 'third_check':
                if not check.operation_ids:
                    raise Warning('You need to make payment first')
                check_type = "rejected"
                debit_account = self.account_id
                credit_account = self.inbank_account_id
                name = _('Check "%s" rejected') % (check.name)
            else:  # issue
                raise Warning(_('You can not reject an Issue Check.'))
        debit_line_vals = {
            'name': name,
            'account_id': debit_account.id,
            'debit': check.amount,
            'credit': 0.0,
            'amount_currency': check.amount_currency,
            'currency_id': check.journal_id.currency_id and check.journal_id.currency_id.id,
            'partner_id': self.partner_id and self.partner_id.id or False
        }
        credit_line_vals = {
            'name': name,
            'account_id': credit_account.id,
            'credit': check.amount,
            'debit': 0.0,
            'amount_currency': check.amount_currency,
            'currency_id': check.journal_id.currency_id and check.journal_id.currency_id.id,
            'partner_id': self.partner_id and self.partner_id.id or False
        }
        move_vals = {
            'name': name,
            'journal_id': check.journal_id.id,
            'date': self.date,
            'ref': name,
            'partner_id': self.partner_id.id,
            'line_ids': [(0, 0, debit_line_vals),
                         (0, 0, credit_line_vals)]
        }
        if self.env.context.get('check_validation') == 'three' and action_type == 'returned':
            # Add another entry if it's validation is Three steps on returned action
            three_step_debit_line_vals = {
                'name': name,
                'account_id': self.partner_id.property_account_receivable_id.id,
                'debit': check.amount,
                'credit': 0.0,
                'amount_currency': check.amount_currency,
                'currency_id': check.journal_id.currency_id and check.journal_id.currency_id.id,
                'partner_id': self.partner_id and self.partner_id.id or False
            }
            three_step_credit_line_vals = {
                'name': name,
                'account_id': debit_account.id,
                'credit': check.amount,
                'debit': 0.0,
                'amount_currency': check.amount_currency,
                'currency_id': check.journal_id.currency_id and check.journal_id.currency_id.id,
                'partner_id': self.partner_id and self.partner_id.id or False
            }
            move_vals['line_ids'].append((0, 0, three_step_debit_line_vals))
            move_vals['line_ids'].append((0, 0, three_step_credit_line_vals))
        return {
            'type': check_type,
            'move_vals': move_vals,
            'inbank_account_id': inbank_account_id}
    
    def action_confirm(self):
        """
        confirm choosen account wizard to create this state move
        :return:
        """
        # used to get correct ir properties
        self = self.with_context(
            company_id=self.company_id.id,
            force_company=self.company_id.id,
        )
        for check in self.env['account.check'].browse(
                self._context.get('active_ids', [])):
            # validate check and get move vals
            vals = self.validate_inbank_action(self.action_type, check)
            check_type = vals.get('type', {})
            inbank_account_id = vals.get('inbank_account_id')
            move_vals = vals.get('move_vals')
            move = self.env['account.move'].create(move_vals)
            move.post()
            check.write({'state': check_type})
            if inbank_account_id:
                check.write({'inbank_account_id': inbank_account_id.id})
            op = check._add_operation(check_type, move, partner=self.partner_id, date=self.date)
            write_vals = {'state': op.operation, 'state_string': op.operation}
            if op:
                if self.action_type == 'returned':
                    write_vals['active'] = False
                check.write(write_vals)



