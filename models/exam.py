# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from datetime import datetime

class ExamCalandar(models.Model):
	_inherit = "exam.calandar"

	@api.model 
	def create(self, vals):
		if vals.get('start_date'):
			result1 = self.env['exam.calandar'].sudo().search([('start_date', '<=', vals['start_date'])]).filtered(lambda x: x.end_date and x.end_date >= datetime.strptime(vals.get('start_date'), '%Y-%m-%d').date())
			if result1:
				message = "Un examen existant à la date du "+vals.get('start_date')
				raise UserError(_(message))
		res = super(ExamCalandar, self).create(vals)
		return res

class ExamExam(models.Model):
	_inherit = "exam.exam"

	@api.model 
	def create(self, vals):
		if vals.get('date'):
			active_id = self.exam_calandar_id.id or self._context.get('active_id')
			result1 = self.env['exam.exam'].sudo().search([('date', '=', vals.get('date'))]).filtered(lambda x: x.exam_calandar_id.id != active_id)
			if result1:
				message = "Un examen existant à la date du "+vals.get('date')
				raise UserError(_(message))
		res = super(ExamExam, self).create(vals)
		return res