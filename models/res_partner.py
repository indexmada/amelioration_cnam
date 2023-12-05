# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResPartner(models.Model):
	_inherit = "res.partner"

	note_list_ids = fields.One2many(comodel_name="note.list", inverse_name="partner_id", string="Notes")

	def get_insc_info(self):
		insc_ids = self.env['inscription.edu'].sudo().search([('student_id', '=', self.id), ('name', '!=', False), ('state', 'in', ['pre-inscription', 'accueil', 'account', 'enf'])], order="id DESC")
		return insc_ids[0] if insc_ids else False