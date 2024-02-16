# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

MONTH_LIST = ['', '1-Janvier', '2-Février', '3-Mars', '4-Avril', '5-Mei', '6-Juin', '7-Juillet', '8-Août', '9-Septembre', '10_Octobre', '11-Novembre', '12-Décembre']

STATE_INSC_PAY_SELECT = [('request', 'Report demandé'), ('granted', 'Report accordé'), ('irrecouvrable', 'Irrecouvrable'), 
						('paid', 'Soldé'), ('non-paid', 'Non Soldé')]

class PaymentInscription(models.Model):
	_inherit = "payment.inscription"

	num_engagement = fields.Integer(string="Numéro")

	amount_paid_payment = fields.Monetary(string="Montant Payé", compute = "compute_amount_paid_payment")
	payment_ids = fields.Many2many(string="Payments", compute="compute_payment_val")
	remain_to_pay_payment = fields.Monetary(string="Reste à Payer", compute="compute_remain_to_pay")

	month_stored = fields.Char(string="Mois", compute="compute_month_year_stored", store=True)
	year_stored = fields.Integer(string="Année", compute="compute_month_year_stored", store=True)

	report_date = fields.Date("Date de report")
	report_granted = fields.Boolean("Report Accordé")
	state = fields.Selection(string="Statut", selection=STATE_INSC_PAY_SELECT, compute="change_state", store = True, default='non-paid')

	@api.depends("remain_to_pay_payment", "payment_state", "inscription_id.insc_demande_report", "inscription_id", "report_date", "report_granted")
	def change_state(self):
		for rec in self:
			if rec.remain_to_pay_payment <= 0:
				rec.state = 'paid'
			else:
				if rec.inscription_id.insc_demande_report == True and rec.report_date:
					if rec.report_granted:
						rec.state = 'granted'
					else:
						rec.state = 'request'
				else:
					rec.state = 'non-paid'

	def compute_remain_to_pay(self):
		for record in self:
			record.remain_to_pay_payment = record.cost_devise - record.amount_paid_payment

	def compute_payment_val(self):
		for rec in self:
			pi_ids = self.env['account.payment'].sudo().search([('state', '!=', 'draft')]).filtered(lambda x: rec in x.payment_inscription_ids)
			rec.payment_ids = pi_ids.ids

	def compute_amount_paid_payment(self):
		for rec in self:
			pi_ids = self.env['account.payment'].sudo().search([('state', '!=', 'draft')]).filtered(lambda x: rec in x.payment_inscription_ids)
			if pi_ids:
				amount_paid = 0
				for pi in pi_ids:
					amount_paid += pi.amount

				rec.amount_paid_payment = amount_paid
			else:
				rec.amount_paid_payment = 0

	@api.depends("date")
	def compute_month_year_stored(self):
		for record in self:
			if record.date:
				month = record.date.month
				record.month_stored = MONTH_LIST[month]

				year = record.date.year
				record.year_stored = year
			else:
				record.month_stored = False
				record.year_stored = False

	# def create(self, vals):
	# 	if not vals.get('num_engagement'):
	# 		result = self.env['payment.inscription'].search([], limit = 1, order="num_engagement DESC")
	# 		if result:
	# 			num_engagement = result.num_engagement + 1
	# 		else:
	# 			num_engagement = 1

	# 		vals['num_engagement'] = num_engagement
	# 	res = super(PaymentInscription, self).create(vals)
	# 	return res

	# def write(self, vals):
	# 	if not vals.get('num_engagement'):
	# 		result = self.env['payment.inscription'].search([], limit = 1, order="num_engagement DESC")
	# 		if result:
	# 			num_engagement = result.num_engagement + 1
	# 		else:
	# 			num_engagement = 1

	# 		vals['num_engagement'] = num_engagement
	# 	res = super(PaymentInscription, self).write(vals)
	# 	return res

class AccountPaymen(models.Model):
	_inherit = "account.payment"

	def get_ue_list(self, invoice_ids):
		unit_enseigne_ids = self.env['unit.enseigne'].sudo().search([('invoice_id', 'in', invoice_ids.ids)])
		return unit_enseigne_ids