# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

CASH_VAL = [20000, 10000, 5000, 2000, 1000, 500, 200, 100]

class AccountBankStatement(models.Model):

    _inherit = "account.bank.statement"

    def open_cashbox_id(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        if context.get('balance'):
            context['statement_id'] = self.id
            if context['balance'] == 'start':
                cashbox_id = self.cashbox_start_id.id
                cashbox =self.cashbox_start_id
                if not cashbox_id:
                    cashbox_vals = {
                        'start_bank_stmt_ids': [(4,self.id)],
                    }
                    cashbox = self.env['account.bank.statement.cashbox'].create(cashbox_vals)
                    cashbox_id = cashbox.id


            elif context['balance'] == 'close':
                cashbox_id = self.cashbox_end_id.id
                cashbox =self.cashbox_end_id
                if not cashbox_id:
                    cashbox_vals = {
                        'end_bank_stmt_ids': [(4,self.id)],
                    }
                    cashbox = self.env['account.bank.statement.cashbox'].create(cashbox_vals)
                    cashbox_id = cashbox.id
            else:
                cashbox_id = False
            
            if cashbox_id :
                print('_'*101)
                cashbox = self.env['account.bank.statement.cashbox'].browse(cashbox_id)
                if not cashbox.cashbox_lines_ids:
                    for val in CASH_VAL:
                        self.env['account.cashbox.line'].create({
                            'cashbox_id': cashbox.id ,
                            'coin_value': val,
                            'number': 0,
                            })

            else:
                print('*'*101)
                print('no cashbox')

            action = {
                'name': _('Cash Control'),
                'view_mode': 'form',
                'res_model': 'account.bank.statement.cashbox',
                'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox_footer').id,
                'type': 'ir.actions.act_window',
                'res_id': cashbox_id,
                'context': context,
                'target': 'new'
            }

            return action