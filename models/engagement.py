# -*- coding: utf-8 -*-

from odoo import models, fields, api

class XlsComparison(models.Model):
    _name = "recap.engagement"
    _description = "Tableau Recapitulatif Engagement"

    school_year = fields.Many2one(string="Années Universitaire", comodel_name="school.year")

    def generate_report(self):
        school_year = str(self.school_year.id)
        str_semester = ''
        actions = {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/web/binary/download_recap_engagement_xls_file?school_year='
                   + school_year
        }
        return actions