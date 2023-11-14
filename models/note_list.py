# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class NoteList(models.Model):
	_inherit = "note.list"

	code_ue_stored = fields.Char(string="Code UE", compute="compute_code_ue_intitule_ue", store=True)
	intitule_ue_stored = fields.Char(string="Intitulé UE", compute="compute_code_ue_intitule_ue", store=True)
	session_stored = fields.Char(string="Session", compute="compute_session_value", store=True)

	@api.depends('unit_enseigne')
	def compute_code_ue_intitule_ue(self):
		for record in self:
			record.code_ue_stored = record.unit_enseigne.code
			record.intitule_ue_stored = record.unit_enseigne.name

	@api.depends("note_list_filter_id", "note_list_filter_id.session", "note_list_filter_id.session.name")
	def compute_session_value(self):
		for record in self:
			record.session_stored = record.note_list_filter_id.session.name

class NoteListFilter(models.Model):
	_inherit = "note.list.filter"

	def get_ue_ids(self, session = 1, year):
		result = self.sudo()search([('year', '=', year)]).filtered(lambda x: x.session.name.find(str(session)) >= 0).mapped('unit.enseigne')
		return result