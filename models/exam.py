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
		res = super(ExamExam, self).create(vals)
		if vals.get('exam_calandar_id') and vals.get('ue_ids') and vals.get('centre_ue_id') and vals.get('date') and vals.get('start_time') and vals.get('end_time'):
			calandar_id = self.exam_calandar_id or self.env['exam.calandar'].sudo().browse(vals.get('exam_calandar_id'))
			school_year = calandar_id.school_year

			unit_enseignes_obj = self.env['inscription.edu'].search([('state','in',('enf','accueil','account')), ('school_year', '=', school_year.id)]).mapped('units_enseignes')
			other_ues_obj = self.env['inscription.edu'].search([('state','in',('enf','accueil','account')), ('school_year', '=', school_year.id)]).mapped('other_ue_ids')
			unit_enseignes_obj |= other_ues_obj

			ue_ids = self.env['unit.enseigne.config'].sudo().search([('id', 'in', vals.get('ue_ids')[0][2])])
			center_ue_id = self.env['examen.center'].sudo().browse(vals.get('centre_ue_id'))

			temp_insc_ids = unit_enseignes_obj.filtered(lambda u: u.name in ue_ids and center_ue_id.id == u.center_id.id and ((calandar_id.semester == u.semestre_id) or (calandar_id.semester_annuel and calandar_id.semester_annuel == u.semestre_id))).mapped('inscription_id')
			temp_insc_ids |= unit_enseignes_obj.filtered(lambda u: u.name in ue_ids and center_ue_id.id == u.center_id.id and ((calandar_id.semester == u.semestre_id) or (calandar_id.semester_annuel and calandar_id.semester_annuel == u.semestre_id))).mapped('inscription_other_id')

			center_ids = calandar_id.center_ids

			insc_ids = temp_insc_ids.filtered(lambda insc: insc.region_center_id in center_ids)
			
			date_value = datetime.strptime(vals.get('date'), "%Y-%m-%d").date()

			exam_repartition_obj = self.env['exam.repartition']

			exam_repartition_ids = exam_repartition_obj.sudo().search([('exam_id', '!=', False)]).filtered(lambda x: x.exam_id.date == date_value and exam_repartition_obj.there_is_overlap(x.exam_id.start_time, x.exam_id.end_time, vals.get('start_time'), vals.get('end_time')) and x.inscription_id in insc_ids)
			if exam_repartition_ids:
				exam_rep_id = exam_repartition_ids[0]
				str_start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(exam_rep_id.exam_id.start_time * 60, 60))
				str_end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(exam_rep_id.exam_id.end_time * 60, 60))
				message = "Un examen existant à la date du "+date_value.strftime('%d/%m/%Y')+" "+str_start_time+" à "+str_end_time+" Pour: "+exam_rep_id.inscription_id.display_name+" ("+exam_rep_id.inscription_id.name+")"
				raise UserError(_(message))

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