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

class ExamRepartition(models.Model):
	_inherit = "exam.repartition"

	@api.model
	def create(self, vals):
		print('__'*50)
		res = super(ExamRepartition, self).create(vals)
		exam_id = self.env['exam.exam'].sudo().browse(vals.get('exam_id'))
		inscription_id = self.inscription_id or self.env['inscription.edu'].sudo().browse(vals.get('inscription_id'))
		exam_repartition_ids = self.search([('exam_id', '!=', exam_id.id), ('exam_id', '!=', False)]).filtered(lambda x: x.exam_id.date == exam_id.date and self.there_is_overlap(x.exam_id.start_time, x.exam_id.end_time, exam_id.start_time, exam_id.end_time) and x.inscription_id == inscription_id)
		if exam_repartition_ids:
			exam_rep_id = exam_repartition_ids[0]
			str_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(exam_rep_id.exam_id.start_time * 60, 60))
			str_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(exam_rep_id.exam_id.end_time * 60, 60))
			message = "Un examen existant à la date du "+exam_id.date.strftime('%d/%m/%Y')+" "+str_start_time+" à "+str_end_time+" Pour: "+exam_rep_id.inscription_id.display_name+" ("+exam_rep_id.inscription_id.name+")"
			raise UserError(_(message))
		return res

	def there_is_overlap(self, nb1,nb2,ch3,ch4):
		return not((nb1 < ch3 and nb2 < ch3) or (nb1 > ch4 and nb2 > ch4))