# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

SELECTION_STATE = [
    ('pre-inscription', 'Pré-inscription'),
    ('accueil', 'Validé Acceuil'),
    ('account', 'Validé comptable'),
    ('enf', 'Validé ENF'),
    ('cancel', 'Annulé')
]

class UnitEnseigneConfig(models.Model):
    _inherit = "unit.enseigne"

    def get_default_global_insc(self):
        global_insc_stored = self.inscription_id or self.inscription_other_id
        self.global_insc_stored = global_insc_stored
        return global_insc_stored

    ue_state = fields.Selection(string="STATUT", selection=SELECTION_STATE, default="pre-inscription", tracking=True, track_visibility='always')
    is_allowed_group_user = fields.Boolean(string="Groups", compute="compute_groupes")
    global_insc_stored = fields.Many2one("inscription.edu", string="Etudiants", compute="get_global_insc_stored", default=get_default_global_insc, store=True)

    school_year = fields.Many2one("school.year", string="Année Universitaire", compute="compute_school_year", store=True)

    def compute_groupes(self):
        for rec in self:
            if rec.ue_state == "pre-inscription":
                if self.env.user.has_group('amelioration_cnam.group_ue_validator'):
                    rec.is_allowed_group_user = True
                else:
                    rec.is_allowed_group_user = False
            elif rec.ue_state == "accueil":
                if self.env.user.has_group('amelioration_cnam.group_ue_validator_compta'):
                    rec.is_allowed_group_user = True
                else:
                    rec.is_allowed_group_user = False
            elif rec.ue_state == "account":
                if self.env.user.has_group('amelioration_cnam.group_ue_validator_enf'):
                    rec.is_allowed_group_user = True
                else:
                    rec.is_allowed_group_user = False
            else:
                rec.is_allowed_group_user = False

    # @api.onchange('inscription_id', 'inscription_other_id', 'name', 'semestre_id', 'year')
    # def insc_change(self):
    #     for record in self:
    #         insc_id = record.inscription_id or record.inscription_other_id
    #         record.ue_state = insc_id.state

    @api.onchange("name")
    def amel_name_change(self):
        for rec in self:
            if rec.name:
                rec.semestre_id = rec.name.semestre_id
            else:
                rec.semestre_id = None


    @api.onchange("name")
    def change_domaine(self):
        return {'domain':{'semestre_id':[('id','=',self.name.semestre_id.id)]}}
        

    @api.depends('inscription_id', 'inscription_other_id')    
    def get_global_insc_stored(self):
        for record in self:
            record.global_insc_stored = record.inscription_id or record.inscription_other_id

    @api.depends('inscription_id', 'inscription_other_id', 'inscription_id.school_year', 'inscription_other_id.school_year')
    def compute_school_year(self):
        for record in self:
            record.school_year = record.global_insc_stored.school_year


class InscriptionEdu(models.Model):
    _inherit = "inscription.edu"

    connaissance_cnam = fields.Selection(selection_add=[('fb', 'Réseaux sociaux')])

    display_name = fields.Char(compute='compute_display_name', store=True)

    # Dossier Incomplets dans Inscription
    degree_certified = fields.Boolean("Photocopie certifiée des diplômes")
    cv_lm = fields.Boolean("CV et Lettre de motivation")
    job_certificate = fields.Boolean("Attestation d'emploi et bulletin de salaire")
    recent_id_photo = fields.Boolean("02 photographies d'identité récentes")
    a4_enveloppes = fields.Boolean("4 enveloppes de format A4")
    cin = fields.Boolean("Photocopie de la carte d'identité ou acte d'état civil (si mineur)")
    residence = fields.Boolean("Certificat de résidence")
    ves = fields.Boolean("Pour VES: joindre le programme détaillé de la formation suivie")

    def send_mail_file_required(self):
        domain = ['|','|','|','|','|','|','|',('degree_certified', '=', False), ('cv_lm', '=', False), 
                    ('job_certificate', '=', False), ('recent_id_photo', '=', False), ('a4_enveloppes', '=', False), 
                    ('cin', '=', False), ('residence', '=', False), ('ves', '=', False)]
        inscription_ids = self.search(domain)
        template = self.env.ref("amelioration_cnam.file_required_email_template")

        for insc in  inscription_ids:

            if insc.email:
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
                    'student_id': insc.student_id,
                }
                with self.env.cr.savepoint():
                    template.with_context(context).send_mail(insc.id, force_send=True, raise_exception=True)
                    values = template.generate_email(insc.id)

    def open_student_info(self):
        if not self.student_id:
            return False

        note_list_ids = self.env['note.list'].search([('partner_id', '=', self.student_id.id)])
        return {
            "name": "Historique Cursus",
            'view_mode': 'list',
            'res_model': 'note.list',
            'type': 'ir.actions.act_window',
            "domain": [('id', 'in', note_list_ids.ids)],
            "context": {'search_default_groupe_by_ue': 1},
        }