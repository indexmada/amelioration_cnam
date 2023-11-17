# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class NoteList(models.Model):
	_inherit = "note.list"

	code_ue_stored = fields.Char(string="Code UE", compute="compute_code_ue_intitule_ue", store=True)
	intitule_ue_stored = fields.Char(string="Intitulé UE", compute="compute_code_ue_intitule_ue", store=True)
	session_stored = fields.Char(string="Session", compute="compute_session_value", store=True)

	note_session1 = fields.Float("Note Session1", compute="compute_note_session")
	note_session2 = fields.Float("Note Session2", compute="compute_note_session")
	note_2set = fields.Boolean(string="Session 2 Set", compute="compute_note_2set", store=True)

	@api.depends('session_stored', 'note_session1', 'note_session2')
	def compute_note_2set(self):
		for rec in self:
			if rec.session_stored and rec.session_stored.find('1')>= 0:
				note_session2 = rec.get_note_other_session()
				if note_session2:
					rec.note_2set = True
				else:
					rec.note_2set = False
			else:
				rec.note_2set = False

	def compute_note_session(self):
		for rec in self:
			if rec.session_stored and rec.session_stored.find('1')>= 0:
				rec.note_session1 = rec.note_sem1 or rec.note_sem2
				rec.note_session2 = rec.get_note_other_session()
			elif rec.session_stored and rec.session_stored.find('2')>= 0:
				rec.note_session1 = rec.get_note_other_session()
				rec.note_session2 = rec.note_sem1 or rec.note_sem2

			else:
				rec.note_session1 = rec.note_sem1 or rec.note_sem2
				rec.note_session2 = 0
	def get_note_other_session(self):
		note_other_session = self.env['note.list'].sudo().search([('partner_id', '=', self.partner_id.id), 
											('unit_enseigne', '=', self.unit_enseigne.id), 
											('years_id', '=', self.years_id.id), 
											('note_list_filter_id', '!=', self.note_list_filter_id.id), 
											('id', '!=', self.id)], limit=1)
		return (note_other_session.note_sem1 or note_other_session.note_sem2) if note_other_session else 0

	@api.depends('unit_enseigne')
	def compute_code_ue_intitule_ue(self):
		for record in self:
			record.code_ue_stored = record.unit_enseigne.code
			record.intitule_ue_stored = record.unit_enseigne.name

	@api.depends("note_list_filter_id", "note_list_filter_id.session", "note_list_filter_id.session.name")
	def compute_session_value(self):
		for record in self:
			record.session_stored = record.note_list_filter_id.session.name

	def get_insc(self):
		insc_id = self.env['inscription.edu'].sudo().search([('student_id', '=', self.partner_id.id)], order="id DESC", limit=1)
		return insc_id

class NoteListFilter(models.Model):
	_inherit = "note.list.filter"

	def get_ue_ids(self, year, session = 1):
		result = self.sudo().search([('year', '=', year)]).filtered(lambda x: x.session.name.find(str(session)) >= 0).mapped('unit_enseigne')
		return result