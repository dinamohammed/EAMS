# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
_STAGES = [
    ('draft', 'Draft'),
    ('holding', 'Holding'),
    ('deposited', 'Deposited'),
    ('selled', 'Sell'),
    ('delivered', 'Delivered'),
    ('transfered', 'Transferred'),
    ('reclaimed', 'Reclaimed'),
    ('withdrawed', 'Withdraw'),
    ('handed', 'Handed'),
    ('under_collection', 'Under Collection'),
    ('inbank', 'Inbank'),
    ('debited', 'Debited'),
    ('returned', 'Returned'),
    ('changed', 'Changed'),
    ('rejected', 'Rejected'),
    ('cancel', 'Cancel'),
]


class AccountCheckOperation(models.Model):
    _name = 'account.check.operation'
    _rec_name = 'operation'
    _order = 'date desc, id desc'
    # _order = 'create_date desc'
    
    # al final usamos solo date y no datetime porque el otro dato ya lo tenemos
    # en create_date. ademas el orden es una mezcla de la fecha el id
    # y entonces la fecha la solemos computar con el payment date para que
    # sea igual a la fecha contable (payment date va al asiento)
    date = fields.Date(
        default=lambda self: fields.Date.today(),
        required=True,
    )
    check_id = fields.Many2one(
        'account.check',
        'Check',
        required=True,
        ondelete='cascade',
        auto_join=True,
    )
    operation = fields.Selection(_STAGES, required=True)
    
    origin_name = fields.Char(
        compute='_compute_origin_name'
    )
    origin = fields.Reference(
        string='Origin Document',
        selection='_reference_models')
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
    )
    notes = fields.Text(
    )
    
    def unlink(self):
        for rec in self:
            if rec.origin:
                raise ValidationError(_(
                    'You can not delete a check operation that has an origin.'
                    '\nYou can delete the origin reference and unlink after.'))
        return super(AccountCheckOperation, self).unlink()
    
    @api.depends('origin')
    def _compute_origin_name(self):
        """
        We add this computed method because an error on tree view displaying
        reference field when destiny record is deleted.
        As said in this post (last answer) we should use name_get instead of
        display_name
        https://www.odoo.com/es_ES/forum/ayuda-1/question/
        how-to-override-name-get-method-in-new-api-61228
        """
        for rec in self:
            try:
                if rec.origin:
                    id, name = rec.origin.name_get()[0]
                    origin_name = name
                    # origin_name = rec.origin.display_name
                else:
                    origin_name = False
            except Exception as e:
                _logger.exception(
                    "Compute origin on checks exception: %s" % e)
                # if we can get origin we clean it
                rec.write({'origin': False})
                origin_name = False
            rec.origin_name = origin_name
    
    @api.model
    def _reference_models(self):
        return [
            ('account.payment', 'Payment'),
            ('account.check', 'Check'),
            ('account.move', 'Invoice'),
            ('account.move', 'Journal Entry'),
            ('account.move.line', 'Journal Item'),
        ]


class AccountCheck(models.Model):
    
    _name = 'account.check'
    _description = 'Account Check'
    _order = "id desc"
    _inherit = ['mail.thread']
    
    operation_ids = fields.One2many(
        'account.check.operation',
        'check_id',
    )
    name = fields.Char(
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    number = fields.Integer(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False
    )
    checkbook_id = fields.Many2one(
        'account.checkbook',
        'Checkbook',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    type = fields.Selection(
        [('issue_check', 'Issue Check'), ('third_check', 'Received Check')],
        readonly=True,
    )
    partner_id = fields.Many2one(comodel_name='res.partner', string="Check Partner")
    inbank_account_id = fields.Many2one('account.account', string='In Bank Account')
    active = fields.Boolean(string="Active", default=True,)
    check_validation = fields.Selection([('two', 'Two Steps'), ('three', 'Three Steps')],
                                        compute='_get_check_validation', string="Check Validation",
                                        help="if we select three steps will effect in Customer payment cycle ")
    after_inbank = fields.Boolean()
    
    def _get_check_validation(self):
        check_validation = self.env['ir.config_parameter'].sudo().get_param('check_validation', default='two')
        after_inbank = self.env['ir.config_parameter'].sudo().get_param('after_inbank', False)
        self.check_validation = check_validation
        self.after_inbank = after_inbank
    
    @api.depends('operation_ids.operation', 'operation_ids.date')
    @api.onchange('operation_ids')
    def _compute_state(self):
        for rec in self:
            if rec.operation_ids:
                operation = rec.operation_ids[0].operation
                rec.state = operation
                rec.state_string = operation.upper()
            else:
                rec.state = 'draft'
                rec.state_string = 'draft'.upper()
    
    state = fields.Selection(_STAGES, default='draft', compute=_compute_state,
                             required=True, copy=False, store=False)
    
    state_string = fields.Char(compute=_compute_state)
    
    issue_date = fields.Date(
        'Issue Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.context_today,
    )
    owner_vat = fields.Char(
        'Owner Vat',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    owner_name = fields.Char(
        'Owner Name',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    bank_id = fields.Many2one(
        'res.bank', 'Bank',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    
    amount = fields.Monetary(
        currency_field='company_currency_id',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    amount_currency = fields.Monetary(
        currency_field='currency_id',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    currency_id = fields.Many2one(
        'res.currency',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    payment_date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        domain=[('type', 'in', ['cash', 'bank'])],
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    company_id = fields.Many2one(
        related='journal_id.company_id',
        readonly=True,
        store=True,
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
    )
    
    @api.constrains('issue_date', 'payment_date')
    @api.onchange('issue_date', 'payment_date')
    def onchange_date(self):
        for rec in self:
            if (
                    rec.issue_date and rec.payment_date and
                    rec.issue_date > rec.payment_date):
                raise UserError(
                    _('Check Payment Date must be greater than Issue Date'))
    
    @api.constrains(
        'type',
        'number',
    )
    def issue_number_interval(self):
        for rec in self:
            # if not range, then we dont check it
            if rec.type == 'issue_check' and rec.checkbook_id.range_to:
                if rec.number > rec.checkbook_id.range_to:
                    raise UserError(_(
                        "Check number (%s) can't be greater than %s on "
                        "checkbook %s (%s)") % (
                                        rec.number,
                                        rec.checkbook_id.range_to,
                                        rec.checkbook_id.name,
                                        rec.checkbook_id.id,
                                    ))
                elif rec.number == rec.checkbook_id.range_to:
                    rec.checkbook_id.state = 'used'
        return False
    
    @api.constrains(
        'type',
        'owner_name',
        'bank_id',
    )
    def _check_unique(self):
        for rec in self:
            if rec.type == 'issue_check':
                same_checks = self.search([
                    ('checkbook_id', '=', rec.checkbook_id.id),
                    ('type', '=', rec.type),
                    ('number', '=', rec.number),
                ])
                same_checks -= self
                if same_checks:
                    raise ValidationError(_(
                        'Check Number (%s) must be unique per Checkbook!\n'
                        '* Check ids: %s') % (
                                              rec.name, same_checks.ids))
            elif self.type == 'third_check':
                same_checks = self.search([
                    ('bank_id', '=', rec.bank_id.id),
                    ('owner_name', '=', rec.owner_name),
                    ('type', '=', rec.type),
                    ('number', '=', rec.number),
                ])
                same_checks -= self
                if same_checks:
                    raise ValidationError(_(
                        'Check Number (%s) must be unique per Owner and Bank!'
                        '\n* Check ids: %s') % (
                                              rec.name, same_checks.ids))
        return True
    
    def _del_operation(self, origin):
        """
        We check that the operation that is being cancel is the last operation
        done (same as check state)
        """
        for rec in self:
            if not rec.operation_ids or rec.operation_ids[0].origin != origin:
                raise ValidationError(_(
                    'You can not cancel this operation because this is not '
                    'the last operation over the check. Check (id): %s (%s)'
                ) % (rec.name, rec.id))
            rec.operation_ids[0].origin = False
            rec.operation_ids[0].unlink()
    
    def _add_operation(
            self, operation, origin, partner=None, date=False):
        for rec in self:
            # agregamos validacion de fechas
            date = date or fields.Datetime.now()
            if rec.operation_ids and rec.operation_ids[0].date > date:
                raise ValidationError(_(
                    'The date of a new operation can not be minor than last '
                    'operation date'))
            vals = {
                'operation': operation,
                'date': date,
                'check_id': rec.id,
                'origin': '%s, %i' % (origin._name, origin.id),
                'partner_id': partner and partner.id or False,
            }
            return rec.operation_ids.create(vals)
    
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise ValidationError(
                    _('The Check must be in draft state for unlink !'))
        return super(AccountCheck, self).unlink()
    
    # checks operations from checks
    
    def bank_debit(self):
        self.ensure_one()
        if self.state in ['handed']:
            vals = self.get_bank_vals(
                'bank_debit', self.journal_id)
            action_date = self._context.get('action_date')
            vals['date'] = action_date
            move = self.env['account.move'].create(vals)
            move.post()
            op = self._add_operation('debited', move, date=action_date)
            if op:
                self.write({'state': op.operation, 'state_string': op.operation})
    
    def claim(self):
        if self.state in ['rejected'] and self.type == 'third_check':
            operation = self._get_operation('handed', True)
            return self.action_create_debit_note(
                'reclaimed', 'customer', operation.partner_id)
    
    @api.model
    def _get_checks_to_date_on_state(self, state, date, force_domain=None):
        """
        Devuelve el listado de cheques que a la fecha definida se encontraban
        en el estadao definido.
        Esta función no la usamos en este módulo pero si en otros que lo
        extienden
        La funcion devuelve un listado de las operaciones a traves de las
        cuales se puede acceder al cheque, devolvemos las operaciones porque
        dan información util de fecha, partner y demas
        """
        # buscamos operaciones anteriores a la fecha que definan este estado
        if not force_domain:
            force_domain = []
        operations = self.operation_ids.search([
                                                   ('date', '<=', date),
                                                   ('operation', '=', state)] + force_domain)
        
        for operation in operations:
            # buscamos si hay alguna otra operacion posterior para el cheque
            newer_op = operation.search([
                ('date', '<=', date),
                ('id', '>', operation.id),
                ('check_id', '=', operation.check_id.id),
            ])
            # si hay una operacion posterior borramos la op del cheque porque
            # hubo otra operación antes de la fecha
            if newer_op:
                operations -= operation
        return operations
    
    def _get_operation(self, operation, partner_required=False):
        self.ensure_one()
        operation_id = self.operation_ids.search([
            ('check_id', '=', self.id), ('operation', '=', operation)],
            limit=1)
        if not operation_id:
            raise ValidationError(_("No operation of type [%s] found on this check" % operation))
        if partner_required:
            if not operation_id.partner_id:
                raise ValidationError(('The [%s] operation has no partner linked.\n'
                                       'You will need to do it manually.') % operation_id)
        return operation_id
    
    def reject(self):
        """
        Supplier Rejection Action
        :return:
        """
        self.ensure_one()
        if self.state in ['deposited', 'selled', 'delivered', 'handed']:
            operation = self._get_operation(self.state)
            if operation.origin._name == 'account.payment':
                journal = operation.origin.journal_id
                # payment_id = operation.origin
            # for compatibility with migration from v8
            elif operation.origin._name == 'account.move':
                journal = operation.origin.journal_id
                # payment_id = self.env['account.payment'].search([('check_id', '=', self.id)], limit=1)
            else:
                raise ValidationError((
                    'The deposit operation is not linked to a payment.'
                    'If you want to reject you need to do it manually.'))
            vals = self.get_bank_vals('bank_reject', journal)
            action_date = self._context.get('action_date')
            vals['date'] = action_date
            move = self.env['account.move'].create(vals)
            move.post()
            # Rest Payment to draft
            # if payment_id:
            #     payment_id.action_draft()
            op = self._add_operation('rejected', move, date=action_date)
            if op:
                self.write({'state': op.operation, 'state_string': op.operation, 'active': False})
            return True
        # elif self.state in ['delivered', 'handed']:
        #     operation = self._get_operation(self.state, True)
        #     self.write({'active': False})
        #     return self.action_create_debit_note(
        #         'rejected', 'supplier', operation.partner_id)
    
    def action_create_debit_note(self, operation, partner_type, partner):
        self.ensure_one()
        action_date = self._context.get('action_date')
        
        if partner_type == 'supplier':
            invoice_type = 'in_invoice'
            journal_type = 'purchase'
            view_id = self.env.ref('account.view_move_form').id
        else:
            invoice_type = 'out_invoice'
            journal_type = 'sale'
            view_id = self.env.ref('account.view_move_form').id
        
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', journal_type),
        ], limit=1)
        name = _('Check "%s" rejection') % (self.name)
        inv_line_vals = {
            'name': name,
            'account_id': self.journal_id._get_check_account('rejected').id,
            'price_unit': (
                    self.amount_currency and self.amount_currency or self.amount),
        }
        
        inv_vals = {
            'ref': name,
            'invoice_date': action_date,
            'invoice_origin': _('Check nbr (id): %s (%s)') % (self.name, self.id),
            'journal_id': journal.id,
            'partner_id': partner.id,
            'type': invoice_type,
            'invoice_line_ids': [(0, 0, inv_line_vals)],
        }
        if self.currency_id:
            inv_vals['currency_id'] = self.currency_id.id
        # we send internal_type for compatibility with account_document
        invoice = self.env['account.move'].with_context(
            internal_type='debit_note').create(inv_vals)
        op = self._add_operation(operation, invoice, partner, date=action_date)
        if op:
            self.write({'state': op.operation, 'state_string': op.operation})
        return {
            'name': name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': view_id,
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }
    
    def get_bank_vals(self, action, journal):
        self.ensure_one()
        # TODO improove how we get vals, get them in other functions
        if action == 'bank_debit':
            # tenemos que usar esa misma
            credit_account = journal.default_debit_account_id
            # la contrapartida es la cuenta que reemplazamos en el pago
            debit_account = self.journal_id._get_check_account('deferred')
            name = _('Check "%s" debit') % (self.name)
        elif action == 'bank_reject':
            credit_account = self.partner_id.property_account_payable_id
            debit_account = self.journal_id._get_check_account('rejected')
            name = _('Check "%s" rejection') % (self.name)
        else:
            raise ValidationError(_(
                'Action %s not implemented for checks!') % action)
        if not debit_account or not credit_account:
            raise Warning(_("Something went wrong with default accounts!!!\n Please Contact your admin Or check accounts "))
        
        debit_line_vals = {
            'name': name,
            'account_id': debit_account.id,
            # 'partner_id': partner,
            'debit': self.amount,
            'amount_currency': self.amount_currency,
            'currency_id': journal.currency_id and journal.currency_id.id,
            # 'ref': ref,
        }
        credit_line_vals = {
            'name': name,
            'account_id': credit_account.id,
            # 'partner_id': partner,
            'credit': self.amount,
            'amount_currency': self.amount_currency,
            'currency_id': journal.currency_id and journal.currency_id.id,
            # 'ref': ref,
        }
        return {
            'ref': name,
            'journal_id': journal.id,
            'date': fields.Date.today(),
            'line_ids': [
                (0, False, debit_line_vals),
                (0, False, credit_line_vals)],
        }
    
    def open_wizard_after_handed_check(self):
        """
        open wizard to chose account of debit
        :return:
        """
        action = self.env.ref('account_check.action_wizard_inbank')
        result = action.read()[0]
        res = self.env.ref('account_check.check_action_inbank_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        result['context'] = {
            'default_action_type': self.env.context.get('default_action_type'),
            'default_journal_id': self.journal_id and self.journal_id.id or False,
            'check_validation': self.check_validation,
            'default_account_id': self.journal_id.default_debit_account_id and
                                  self.journal_id.default_debit_account_id.id or False,
            'default_partner_id': self.partner_id and self.partner_id.id}
        return result
    
    def bank_debit_action(self):
        """
        open wizard to choose journal for debit account
        :return:
        """
        self.ensure_one()
        action = self.env.ref('account_check.action_wizard_inbank')
        result = action.read()[0]
        res = self.env.ref('account_check.check_action_inbank_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        result['context'] = {'default_action_type':'bank_debit',
                             'default_inbank_account_id':self.inbank_account_id.id if self.inbank_account_id else False}
        return result
    
    def bank_return_action(self):
        """
		open wizard to choose journal for debit account
		:return:
		"""
        self.ensure_one()
        action = self.env.ref('account_check.action_wizard_inbank')
        result = action.read()[0]
        res = self.env.ref('account_check.check_action_inbank_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        holding_account = self.journal_id._get_check_account('holding')
        result['target'] = 'new'
        result['context'] = {'default_action_type': 'returned',
                             'default_inbank_account_id': self.inbank_account_id.id if self.inbank_account_id else False,
                             'default_partner_id': self.partner_id and self.partner_id.id or False,
                             'default_account_id': holding_account and holding_account.id or False}
        return result
    
    def open_wizard_customer_notes_return(self):
        """
        open wizard to chose account of debit
        :return:
        """
        action = self.env.ref('account_check.action_wizard_inbank')
        result = action.read()[0]
        res = self.env.ref('account_check.check_action_inbank_form_view', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['target'] = 'new'
        result['context'] = {
            'default_action_type': 'returned',
            'default_journal_id': self.journal_id and self.journal_id.id or False,
            'check_validation': self.check_validation,
            'default_partner_id': self.partner_id and self.partner_id.id,
            'default_account_id': self.journal_id.default_debit_account_id and
                                  self.journal_id.default_debit_account_id.id or False,
        }
        return result
    
    def change_state_handed(self):
        """
        on start show button to hand check
        :return:
        """
        if self.state == 'holding'and self.operation_ids:
            for line in self.operation_ids:
                line.write({'operation': 'handed'})
                
    def write(self, vals):
        if 'active' in vals and not vals.get('active'):
            payment_id = self.env['account.payment'].search([('check_name', '=', self.name)])
            if payment_id:
                # payment_id.action_draft()
                payment_id.write({'state': 'rejected'})
        return super(AccountCheck, self).write(vals)


