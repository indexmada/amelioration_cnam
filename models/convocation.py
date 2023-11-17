# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models, _

from datetime import date

class ConvocationList(models.Model):
	_inherit = "convocation.list"

	exam_calandar_id_stored = fields.Many2one(string="Calendrier d'Examen", comodel_name="exam.calandar", compute="compute_exam_calandar", store=True)

	conv_sign = fields.Boolean("Signature Directeur")

	@api.depends("exam_ids", "exam_ids.exam_calandar_id")
	def compute_exam_calandar(self):
		for record in self:
			calandar_id = None
			if record.exam_ids:
				for e in record.exam_ids:
					if e.exam_calandar_id:
						calandar_id = e.exam_calandar_id
			record.exam_calandar_id_stored = calandar_id


	def send_convocation_by_email(self):
		template = self.env.ref("amelioration_cnam.convocation_email_template")
		for convocation in self:
			insc = convocation.inscription_id
			if insc.email:
				pdf = self.env.ref('edu_management.action_report_convocation').render_qweb_pdf(convocation.id)
				b64_pdf = base64.b64encode(pdf[0])
				pdf_name = "Convocation-"+insc.display_name.replace(' ', '_')+'.pdf'

				generated_file = self.env['ir.attachment'].create({
					'name': pdf_name,
					'type': 'binary',
					'datas': b64_pdf,
					'store_fname': pdf_name,
					'res_model': self._name,
					'res_id': convocation.id,
					'mimetype': 'application/x-pdf'
				})

				template.attachment_ids = [(6,0,[generated_file.id])]
				template_values = {
					'email_from': self.env.company.email,
					'email_to': insc.email,
					'email_cc': False,
					'auto_delete': True,
					'partner_to': insc.student_id.id,
					'scheduled_date': False,
				}

				template.write(template_values)
				context = { 
					'lang': self.env.user.lang, 
					'session_name': "Première" if convocation.exam_calandar_id_stored.session.name.find('1')>0 else "Deuxième"
				}
				with self.env.cr.savepoint():
					template.with_context(context).send_mail(convocation.id, force_send=True, raise_exception=True)
					values = template.generate_email(convocation.id)

	@api.onchange("number_convocation", "inscription_id", "fonmation_id", "auditor_number", "address_name", "school_year")
	def change_date_value(self):
		for record in self:
			record.date = date.today()
