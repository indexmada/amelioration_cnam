# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class RecapHonoraire(models.Model):
	_name = "recap.honoraire"
	_description = "Recap Honoraire Tuteur"

	semester_ids = fields.Many2many(comodel_name="semestre.edu", string="Semestres")

	def generate_report(self):
		str_semester = ''
		for rec in self.semester_ids:
			str_semester += '-'+str(rec.id) if str_semester else str(rec.id)
		actions = {
			'type': 'ir.actions.act_url',
			'target': 'current',
			'url': '/web/binary/download_recap_honoraire_tuteur_xlsx?str_semester='+str_semester
		}
		return actions