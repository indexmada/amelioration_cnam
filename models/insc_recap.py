# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models, _

from datetime import date

class InscRecap(models.Model):
	_name="insc.recap"
	_description = "Excel Report Recap. Inscription"

	date_from = fields.Date("Date Debut")
	date_to = fields.Date("Date Fin")

	school_year_ids = fields.Many2many(comodel_name="school.year", string="Année universitaire")

	def generate_report(self):
		if self.school_year_ids:
			str_school_year_ids = ''
			for year in self.school_year_ids:
				str_school_year_ids += str(year.id) + '-'
		else:
			str_school_year_ids = "0"
		str_date_from = self.date_from.strftime("%d-%m-%Y") if self.date_from else False
		str_date_to = self.date_to.strftime("%d-%m-%Y") if self.date_to else False
		url = '/web/binary/download_insc_recap_xls_file?str_school_year_ids=' + str_school_year_ids
		if str_date_from:
			url += "&str_date_from="+str_date_from
		if str_date_to:
			url += "&str_date_to="+str_date_to
		actions = {
			'type': 'ir.actions.act_url',
			'target': 'current',
			'url': url,
		}
		return actions