# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class TrainingEdu(models.Model):
	_inherit = "training.edu"

	attachment_ids = fields.Many2many(string="Documents", comodel_name="ir.attachment")

	def get_all_training_attach(self):
		partner = self.env.user.partner_id
		insc_ids = self.env['inscription.edu'].sudo().search([('student_id', '=', partner.id)])
		formation_attach = insc_ids.mapped('formation_id').filtered(lambda x: x.attachment_ids != False)
		return formation_attach

	def get_doc_training_count(self):
		formation_attach = self.sudo().get_all_training_attach()
		documents_attach = formation_attach.mapped('attachment_ids')
		return len(documents_attach)