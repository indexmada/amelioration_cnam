# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class RegroupingCenterLine(models.Model):
    _inherit = "regrouping.center.line"

    assigned_student = fields.Many2many(comodel_name = "res.partner", compute='compute_assigned_student', store=True)

    tutor_attendance = fields.Many2many(comodel_name="res.tutor", string="Pointage Prof")

    @api.depends('assignement_ids')
    def compute_assigned_student(self):
        for rec in self:
            rec.assigned_student = rec.assignement_ids.mapped('student_id')

    def export_pointage_ue(self):
        report_name = "suivi_presence_ue.xlsx"
        id_tab = False
        for i in self:
            if not id_tab:
                id_tab = str(i.id)
            else:
                id_tab += "_"+str(i.id)
        if not id_tab:
            id_tab=""
        return {
            'type': 'ir.actions.act_url',
            'target': 'current',
            'url': '/export_pointage_ue?file_name='
                   + (report_name or "")+'&id_tab='+id_tab        
        }  