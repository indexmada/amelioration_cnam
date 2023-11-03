# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class NoteList(models.Model):
	_inherit = "note.list"

	code_ue_stored = fields.Char(string="Code UE", compute="compute_code_ue_intitule_ue", store=True)
	intitule_ue_stored = fields.Char(string="Intitulé UE", compute="compute_code_ue_intitule_ue", store=True)

	@api.depends('unit_enseigne')
	def compute_code_ue_intitule_ue(self):
		for record in self:
			record.code_ue_stored = record.unit_enseigne.code
			record.intitule_ue_stored = record.unit_enseigne.name
