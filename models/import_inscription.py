# -*- coding: utf-8 -*-

import base64
from odoo import api, fields, models, _

from datetime import date, datetime
from odoo.exceptions import ValidationError

import openpyxl
import base64
from io import BytesIO


class ImportInscription(models.Model):
	_name = "import.inscription"
	_description = "Import Inscription XLSX"

	def default_last_line(self):
		import_id = self.env["import.inscription"].sudo().search([], order="last_line DESC", limit=1)
		return import_id.last_line or 5

	file = fields.Binary(string="Fichier", readonly=False, store=True, required=True)
	xls_filename = fields.Char(string="Nom Du Fichier", readonly=False, store=True)
	last_line = fields.Integer(string="Dérnière Ligne Importée", default=default_last_line)

	def import_file(self):
		if self.file:
			if not self.xls_filename:
				raise ValidationError(_("Aucun Fichier Réçu!"))
			else:
				# Check the file's extension
				tmp = self.xls_filename.split('.')
				ext = tmp[len(tmp)-1]
				if ext not in ['xlsx', 'xls']:
					raise ValidationError(_("Le fichier doit être un fichier Excel. (.xls, .xlsx)"))

		wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.file)), read_only=True)
		ws = wb.active
		inscription_obj = self.env["inscription.edu"].sudo()
		inscription_ids = self.env["inscription.edu"].sudo()

		last_line = self.last_line + 1
		for record in ws.iter_rows(min_row=last_line, max_row=None, min_col=None, max_col=None, values_only=True):
			if not record[0] and not record[6]:
				continue
			center_id = self.env['region.center'].sudo().search([('name', '=', record[14])], limit = 1)
			if not center_id and record[14]:
				raise ValidationError(_("Centre d'inscription "+record[14]+" n'existe pas!"))

			organisatrice_center_id = self.env['examen.center'].sudo().search([('name', '=', record[15])], limit=1)
			if not organisatrice_center_id:
				raise ValidationError(_("Centre organisatrice "+record[15]+" n'existe pas!"))

			country_id = self.env["res.country"].sudo().search([("name", "=", record[23].capitalize())]) if record[23] else False

			if not record[27]:
				raise ValidationError(_("Colonne Date de naissance est obligatoire"))

			formation_id = self.env["training.edu"].sudo().search([('name', '=', record[31])], limit = 1)
			if not formation_id:
				raise ValidationError(_("Formation :"+record[31]+" n'existe pas!"))

			vals = {
				"name": record[0],
				"type": "re-registration" if record[1] == "oui" else "re-registration",
				"state": "enf" if record[5] else "account" if record[4] else "accueil" if record[3] else "pre-inscription",
				"surname": record[6],
				"name_marital": record[7],
				"firstname": record[8],
				"email": record[9],
				"inscription_date": datetime.strptime(record[13], "%d/%m/%Y").date() if record[13] else '',
				"region_center_id": center_id.id,
				"examen_center_id": organisatrice_center_id.id,
				"adress": record[20],
				"zip": record[21],
				"town": record[22],
				"country_id": country_id.id,
				"phone": record[24],
				"mobile": record[25],
				"sexe": record[26],
				"date_of_birth": datetime.strptime(record[27], "%Y-%m-%d").date() if record[27] else '',
				"place_of_birth": record[28],
				"formation_id": formation_id.id,
			}

			inscription_id = inscription_obj.create(vals)

			# UE
			ue_tab = record[32].split(",")
			unit_enseigne_ids = self.env["unit.enseigne"].sudo()
			for ue in ue_tab:
				ue_id = self.env["unit.enseigne.config"].sudo().search([('code', '=', ue)], limit = 1)
				if not ue_id:
					raise ValidationError(_("UE "+ue+" n'existe pas!"))

				unit_enseigne_vals = {
					"year": ue_id.year,
					"name": ue_id.id,
					"semestre_id": ue_id.semestre_id.id,
					"currency_id": self.env.ref('base.MGA').id,
					"rate": 1,
				}

				unit_enseigne_ids |= self.env["unit.enseigne"].sudo().create(unit_enseigne_vals)
			inscription_id.write({
				"units_enseignes": [(6, 0, unit_enseigne_ids.ids)]
			})

			inscription_ids |= inscription_id

			last_line += 1

		self.write({"last_line": last_line -1})
		return {
			'type': 'ir.actions.act_window',
			'name': _('Inscription Enregistrées'),
			'view_mode': 'tree,form',
			'res_model': 'inscription.edu',
			'target': 'new',
			"domain": [('id', 'in', inscription_ids.ids)],
			"views": [(self.env.ref("edu_management.inscription_edu_tree").id, 'tree'),
						(self.env.ref("edu_management.inscription_edu_form").id, 'form')],
		}