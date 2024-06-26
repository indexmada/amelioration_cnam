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

    ue_state = fields.Selection(string="Statut ue initial", selection=SELECTION_STATE, default="pre-inscription", tracking=True, track_visibility='always')
    ue_state_modif = fields.Selection(string="Statut ue actuel", selection='_get_selection_state', tracking=True, track_visibility='always')
    is_allowed_group_user = fields.Boolean(string="Groups", compute="compute_groupes")
    global_insc_stored = fields.Many2one("inscription.edu", string="Etudiants", compute="get_global_insc_stored", default=get_default_global_insc, store=True)

    school_year = fields.Many2one("school.year", string="Année Universitaire", compute="compute_school_year", store=True)

    def _get_selection_state(self):
        state = []
        if self.env.user.has_group('amelioration_cnam.group_ue_validator'):
            state.append(('accueil','Validé Accueil'))
        if self.env.user.has_group('amelioration_cnam.group_ue_validator_compta'):
            state.append(('account', ('Validé comptable')))
        if self.env.user.has_group('amelioration_cnam.group_ue_validator_enf'):
            state.append(('enf', 'Validé ENF'))

        return state

    def write(self, vals):
        if vals.get('ue_state_modif'):
            vals['ue_state'] = vals.get('ue_state_modif')
        res = super(UnitEnseigneConfig, self).write(vals)
        return res

    @api.onchange('ue_state_modif')
    def change_ue_state(self):
        for rec in self:
            rec.ue_state = rec.ue_state_modif

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
        return {'domain':{'semestre_id':[('id','in',self.name.semestre_ids_new.ids)]}}
        

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

    insc_demande_report = fields.Boolean("Demande report")

    num_engagement = fields.Integer("Numéro Engagement")

    # lettre d'engagement Signature
    le_sign = fields.Boolean("Signature Lettre d'engagement")
    # Certificat de scolarité Signature
    cs_sign = fields.Boolean("Signature Certificat de scolarité")
    rel_note_sign = fields.Boolean("Signature relevé de note")

    note_list_ids = fields.Many2many(comodel_name="note.list", compute="compute_note_list_ids", string="Notes")

    ue_not_used = fields.Many2many(comodel_name="unit.enseigne.config", string="UE NOT USER", compute="compute_ue_not_used", store=True)

    total_amount_du_ariary = fields.Float(string="Non soldé Ariary", compute="compute_sold")
    total_amount_du_euro = fields.Float(string="Non soldé Euro", compute="compute_sold")

    @api.depends("amount_total_ariary", "amount_total_euro", "payment_inscription_ids.amount", 'payment_inscription_ids.state')
    def compute_sold(self):
        currency_euro = self.env.ref('base.EUR')
        currency_ariary = self.env.ref('base.MGA')
        for insc in self:
            paid_ariary = 0
            paid_euro = 0
            for line in insc.payment_inscription_ids:
                if line.currency_id.name == 'MGA' and line.state == 'paid':
                    paid_ariary = paid_ariary + float(line.cost_devise)
                elif line.currency_id.name == 'EUR' and line.state == 'paid':
                    paid_euro = paid_euro + float(line.cost_devise)
            total_amount_du_euro = insc.amount_euro - paid_euro
            insc.total_amount_du_euro = total_amount_du_euro if total_amount_du_euro > 0 else 0
            total_amount_du_ariary = insc.amount_total_ariary - paid_ariary
            insc.total_amount_du_ariary = total_amount_du_ariary if total_amount_du_ariary > 0 else 0

    @api.depends('units_enseignes', 'other_ue_ids', 'formation_id', 'formation_id.units_enseignement_ids')
    def compute_ue_not_used(self):
        for rec in self:
            ue_ids = rec.units_enseignes + rec.other_ue_ids
            ue_config_ids = ue_ids.mapped('name')
            ue_formation_ids = rec.formation_id.units_enseignement_ids

            results = ue_formation_ids.filtered(lambda x: x not in ue_config_ids)
            rec.ue_not_used = results

    def compute_note_list_ids(self):
        for rec in self:
            rec.note_list_ids = rec.student_id.note_list_ids.filtered(lambda x: x.years_id == rec.school_year)

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

    def p_update_pay_insc_state(self, **kw):
        for rec in self.mapped('payment_inscription_ids'):
            state = None
            if rec.report_irrec: 
                state = 'irrecouvrable'
            else:
                if rec.remain_to_pay_payment <= 0:
                    state = 'paid'
                else:
                    if rec.inscription_id.insc_demande_report == True and rec.report_date:
                        if rec.report_granted:
                            state = 'granted'
                        else:
                            state = 'request'
                    else:
                        state = 'non-paid'
            rec.write({'state': state})

    def open_student_info(self):
        if not self.student_id:
            return False

        # note_list_ids = self.env['note.list'].search([('partner_id', '=', self.student_id.id)])
        # return {
        #     "name": "Historique Cursus",
        #     'view_mode': 'list',
        #     'res_model': 'note.list',
        #     'type': 'ir.actions.act_window',
        #     "domain": [('id', 'in', note_list_ids.ids)],
        #     "context": {'search_default_groupe_by_ue': 1},
        # }
        return self.env.ref(
            'amelioration_cnam.action_historique_cursus_report').report_action(self)

    def get_insc_ids(self):
        student_id = self.student_id
        insc_ids = self.search([('student_id', '=', student_id.id), ('state', '!=', 'cancel')], order="school_year ASC")
        return insc_ids

    def show_rel_note_inscription_details(self):
        insc_no_notes = self.sudo().search([]).filtered(lambda insc: insc.note_list_ids)
        return {
            "name": "Relevé de Notes",
            "view_mode": "form,tree",
            "res_model": "inscription.edu",
            "type": "ir.actions.act_window",
            'views': [(self.env.ref('amelioration_cnam.rel_note_tree').id, 'tree'), 
                        (self.env.ref('amelioration_cnam.rel_note_form').id, 'form')],
            "domain": [('id', 'in', insc_no_notes.ids)],
        }

    @api.model
    def create(self, vals):
        res = super(InscriptionEdu, self).create(vals)
        if not vals.get('num_engagement'):
            result = max(self.env['inscription.edu'].search([]).mapped('num_engagement'))
            print('_'*100)
            print(result)
            if result:
                num_engagement = result + 1
            else:
                num_engagement = 1
            print(num_engagement)
            res['num_engagement'] = num_engagement
        return res

    def get_num_engagement(self):
        num = self.num_engagement
        num_str = ''
        ln = len(str(num))
        if ln < 4:
            for i in range(0, 4-ln):
                num_str += '0'

        num_str += str(num)
        return num_str

    def check_le_sign(self):
        for insc in self:
            insc.write({'le_sign': True})

    def uncheck_le_sign(self):
        for insc in self:
            insc.write({'le_sign': False})

    def check_cs_sign(self):
        for insc in self:
            insc.write({'cs_sign': True})

    def uncheck_cs_sign(self):
        for insc in self:
            insc.write({'cs_sign': False})

    def check_rel_note_sign(self):
        for insc in self:
            insc.write({'rel_note_sign': True})

    def uncheck_rel_note_sign(self):
        for insc in self:
            insc.write({'rel_note_sign': False})

    def action_historique_engagement(self):
        str_insc = ''
        for insc in self:
            str_insc += '-'+str(insc.id) if str_insc else str(insc.id)
        school_year = False
        actions = {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/web/binary/download_recap_engagement_xls_file?str_insc='+str_insc
        }
        return actions