# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    school_year_ids = fields.Many2many("school.year", "company_school_year_ids", 
                                                    "company_id", "school_year_id", 'AU (Affichage des Certificats de scolarité dans Espace Elève)')
    date_last = fields.Date("Dernier Affichage")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    school_year_ids = fields.Many2many(related = "company_id.school_year_ids", string="AU (Affichage des Certificats de scolarité dans Espace Elève)", readonly=False)
    date_last = fields.Date(related="company_id.date_last", string="Dernier Affichage", readonly=False)