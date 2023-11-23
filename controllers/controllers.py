# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date


class AmeliorationCnam(http.Controller):
    @http.route('/amelioration_cnam/update_insc_state', auth='public')
    def index(self, **kw):
        ue_ids = request.env['unit.enseigne'].sudo().search(['|', ('inscription_id', '!=', False), ('inscription_other_id', '!=', False)])
        for ue in ue_ids:
            insc_id = ue.inscription_id or ue.inscription_other_id
            ue.sudo().write({'insc_state': insc_id.state})

        return "INSC STATE UPDATED"

    @http.route('/load_ue_section_by_year/<int:year>/<ue_search_val>', auth='public')
    def load_ue_section_by_year(self, year, ue_search_val):
        if ue_search_val == '0' or ue_search_val == 0:
            ue_search_val = False
        year_id = request.env['school.year'].sudo().browse(year)
        vals = {
            'year': year_id,
            'ue_search_val': ue_search_val,
            }
        return request.render('amelioration_cnam.result_template', vals)

    @http.route('/show_result_content/<int:year>/<session>/<int:ue_id>/<num_audit>', auth='public')
    def show_result_content(self, year, session, ue_id, num_audit):
        if num_audit == '0' or num_audit == 0:
            num_audit = False
        ue = request.env['unit.enseigne.config'].sudo().browse(ue_id)
        ue_name = ue.display_name
        note_list_filter_ids = request.env['note.list.filter'].sudo().search([('year', '=', year), ('unit_enseigne', '=', ue_id), ('show_in_website', '=', True)]).filtered(lambda x: x.session.name.find(str(session)) >= 0)
        result_ids = note_list_filter_ids.mapped('note_list_ids')
        if num_audit:
            result_ids = result_ids.filtered(lambda res: res and res.audit and num_audit.lower() in res.audit.lower())
        vals = {
            'note_list_ids': result_ids, 
            'ue_name': ue_name, 
            'ue': ue, 
            'year': year,
            'session': session,
            'num_audit': num_audit
        }
        return request.render('amelioration_cnam.result_content_template', vals)

    @http.route('/amelioration_cnam/update_pay_insc_state', auth='public')
    def update_pay_insc_state(self, **kw):
        records = request.env['payment.inscription'].search([('inscription_id', '!=', False)])
        for rec in records:
            state = None
            if not rec.state:
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
        

        return "PAY INSC STATE UPDATED"

    @http.route('/export_pointage_ue', auth='public')
    def download_suivi_presence_file_excel(self, file_name, id_tab=''):  #
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        self.report_excel_suivi_presence(workbook, id_tab)  
        workbook.close()
        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)

    def report_excel_suivi_presence(self, workbook, id_tab):
        id_tab = id_tab.split('_')
        regrouping_line_ids = False
        ue_config_ids = False
        for i in id_tab:
            reg_line = request.env['regrouping.center.line'].sudo().browse(int(i))
            if not reg_line:
                continue
            if not regrouping_line_ids:
                regrouping_line_ids = reg_line
            else:
                regrouping_line_ids |= reg_line

            if not ue_config_ids:
                ue_config_ids = reg_line.ue_config_id
            else:
                ue_config_ids |= reg_line.ue_config_id

        center_bold_12 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 12,
            "bold": True,
            })
        left_bold_12 = workbook.add_format({
            'align': 'left',
            'valign': 'vleft',
            "font_size": 12,
            "bold": True,
            })

        cell_bold_center_12 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 12,
            "bold": True,
            })

        cell_left_12 = workbook.add_format({
            'align': 'left',
            'valign': 'vleft',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 12,
            })

        cell_center_12 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 12,
        })

        for ue in ue_config_ids:
            worksheet_ost = workbook.add_worksheet(ue.display_name)
            self.style(worksheet_ost)

            line_filtered = request.env['regrouping.center.line'].sudo().search([('id', 'in', regrouping_line_ids.ids), ('ue_config_id', '=', ue.id)], order="grouping_date ASC")
            all_students = line_filtered.mapped('assigned_student')


            logo_image = io.BytesIO(base64.b64decode(request.env.company.logo))
            worksheet_ost.insert_image('H1', "image.png", {'image_data': logo_image,'x_scale': 0.60,'y_scale':0.60})
            worksheet_ost.write("A2", ue.display_name, center_bold_12)
            worksheet_ost.write("A3", "Tuteur: ", left_bold_12)

            worksheet_ost.write("A5", "Nom et Prénoms", cell_bold_center_12)

            row_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']

            line = 6
            for student in all_students:
                cell = 'A'+str(line)
                worksheet_ost.write(cell, student.name, cell_left_12)
                line += 1
            cell = 'A'+str(line)
            worksheet_ost.write(cell, '', cell_left_12)

            i = 1
            for l in line_filtered:
                cell = row_tab[i]+'5'
                worksheet_ost.write(cell, str(l.grouping_date).replace('-', '/'), cell_bold_center_12)
                line = 6
                for student in all_students:
                    assignement_student = l.assignement_ids.filtered(lambda x: x.student_id == student)
                    c = row_tab[i]+str(line)
                    if assignement_student in l.student_pointed_ids:
                        worksheet_ost.write(c, '1', cell_center_12)

                    else:
                        worksheet_ost.write(c, '', cell_center_12)
                    line += 1
                cell = row_tab[i]+str(line)
                worksheet_ost.write(cell, len(l.student_pointed_ids), cell_center_12)

                i+=1



    def style(self, worksheet):
        worksheet.set_column('A:A', 33)
        worksheet.set_column('B:AM', 14)

