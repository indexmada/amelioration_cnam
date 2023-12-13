# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResTutor(models.Model):
	_inherit = "res.tutor"

	def action_pointage_par_prof(self):
		str_tutor = ''
		for tutor in self:
			str_tutor += '-'+str(tutor.id) if str_tutor else str(tutor.id)
		actions = {
			'type': 'ir.actions.act_url',
			'target': 'current',
			'url': '/web/binary/download_res_tutor_xls_file?str_tutor='+str_tutor
		}
		return actions