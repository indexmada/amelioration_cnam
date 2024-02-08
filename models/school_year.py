# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

AS_VALUE = ["2018-2019","2019-2020","2020-2021","2021-2022","2022-2023","2023-2024",
			"2024-2025","2025-2026","2026-2027","2027-2028", "2028-2029","2029-2030""2030-2031"]

from odoo import fields, models

class SchoolYear(models.Model):
	_inherit ="school.year"
	enipa = fields.Many2many(comodel_name="res.partner", string="Non Inscrits", compute="compute_enipa")

	def compute_enipa(self):
		for rec in self:
			as_val = AS_VALUE
			try:
				key = as_val.index(rec.name)
			except:
				key = False
			if key:
				# Operation
				inscription_ids = self.env['inscription.edu'].sudo().search([('school_year', '=', rec.id), ('state', 'in', ['accueil', 'account', 'enf', 'pre-inscription'])])

				as_last = self.sudo().search([('name', '=', as_val[key-1])])
				last_inscription_ids = self.env['inscription.edu'].sudo().search([('school_year', '=', as_last.id), ('state', 'in', ['accueil', 'account', 'enf', 'pre-inscription'])])

				res = last_inscription_ids.filtered(lambda x: x.student_id not in inscription_ids.mapped('student_id')).mapped('student_id')

			else:
				res = None

			rec.enipa = res