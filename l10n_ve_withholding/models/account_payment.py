# -*- coding: utf-8 -*-
##############################################################################
# Author: SINAPSYS GLOBAL SA || MASTERCORE SAS
# Copyleft: 2022-Present.
#
#
###############################################################################
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    #created to record retention percentages
    comment_withholding = fields.Char('Comment withholding')
    concept_withholding = fields.Char('Concept withholding')
    withholding_distribution = fields.Boolean(
        'tiene una distribucion de retencion?')
    withholding_distribution_ids = fields.One2many(
        'withholding.distribution', 'payment_id',
        string='distribucion de retencion'
    )

    def _get_fiscal_period(self, date):
        str_date = str(date).split('-')
        vals = 'AÑO '+str_date[0]+' MES '+str_date[1]
        return vals

    @api.onchange('journal_id')
    def _onchange_compute_amount_currency(self):
        for rec in self:
            pass
            if rec.other_currency and rec.payment_group_id:
                if rec.payment_group_id.payments_amount <= 0:
                    rec.amount = rec.payment_group_id.selected_finacial_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    rec.amount = 0
                    payments_amount = rec.payment_group_id.selected_finacial_debt - \
                        rec.payment_group_id.payments_amount
                    rec.amount = rec.company_id.currency_id._convert(
                        payments_amount, rec.currency_id, rec.company_id, rec.date)
            if not rec.other_currency and rec.payment_group_id:
                rec.amount = rec.payment_group_id.selected_finacial_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    payments_amount = rec.payment_group_id.payments_amount - rec.amount
                    rec.amount = rec.payment_group_id.selected_finacial_debt - \
                        payments_amount

    @api.onchange('date')
    def _onchange_compute_amount_currency_date(self):
        for rec in self:
            if rec.other_currency and rec.payment_group_id:
                rec.amount_company_currency = rec.currency_id._convert(
                    rec.amount, rec.company_id.currency_id,
                    rec.company_id, rec.date)

    def action_post(self):
        for pay in self:
            if pay.payment_group_id and pay.payment_group_id.to_pay_move_line_ids:
                to_pay = pay.payment_group_id.to_pay_move_line_ids[0]
                if to_pay.move_id.move_type == 'in_refund' and  pay.computed_withholding_amount:
                    pay.write({
                        'payment_type': 'inbound',
                    })
        return super(AccountPayment, self).action_post()

    def get_sustraendo(self):
        if self.concept_withholding:
            code_seniat = self.concept_withholding.split(' - ')[0]
            activity_name = self.concept_withholding.split(' - ')[1]
            regimen_id = self.env['seniat.tabla.islr']\
                .search([('code_seniat','=',code_seniat), 
                            ('activity_name','=',activity_name)],limit=1)
            if regimen_id:
                if regimen_id.type_subtracting == 'amount':
                    return self.format_miles_number(regimen_id.banda_calculo_ids[0].withholding_amount)
        return False