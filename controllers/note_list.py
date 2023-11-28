# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date, datetime

class NoteList(http.Controller):

    @http.route('/web/binary/export_pv_note_excel', auth='public')
    def download_excel_pv_note(self, id_tab=''):  #
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        file_name = "PV_NOTE.xlsx"

        self.report_excel_pv_note(workbook, id_tab)  
        workbook.close()
        output.seek(0)
        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)

    def report_excel_pv_note(self, workbook, id_tab):
        id_tab = id_tab.split('-')
        id_tab.pop()
        res_ids = [eval(i) for i in id_tab]
        note_list_filter_ids = request.env['note.list.filter'].sudo().search([('id', 'in', res_ids)])

        cell_11_bold_center = workbook.add_format({
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
            "font_size": 11,
            "bold": True,
            })
        left_11 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            "font_size": 11,
            })

        left_10 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            "font_size": 10,
            })

        cell_header = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 11,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            'bg_color': '#ffff00',
            })
        cell_11_left = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            'font_size': 11,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            })

        left_8_italic = workbook.add_format({
                    'align': 'left',
                    'valign': 'vcenter',
                    'font_size': 8,
                    'italic': True
                })
        for note_id in note_list_filter_ids:
            ue = note_id.unit_enseigne
            worksheet_ost = workbook.add_worksheet(ue.display_name+' ('+str(note_id.id)+')')
            self.style(worksheet_ost)
            logo_image = io.BytesIO(base64.b64decode(request.env.company.logo))
            worksheet_ost.insert_image('A1', "image.png", {'image_data': logo_image,'x_scale': 0.60,'y_scale':0.60})
            worksheet_ost.merge_range("A7:D7", "PROCES VERBAL DE RESULTATS D'EXAMEN", cell_11_bold_center)
            worksheet_ost.merge_range("A8:C8", "CODE UE : "+ue.code, left_11)
            worksheet_ost.merge_range("A9:C9", "Année universitaire : "+note_id.year.name, left_11)
            worksheet_ost.write("D9", note_id.session.name, left_11)
            worksheet_ost.merge_range("A10:C10", "Enseignant : "+(note_id.tutor_id.name if note_id.tutor_id else ''), left_11)

            # FILL HEADER
            line = 12
            header_tab = ["N° Auditeur", "Noms", "Prénoms", "Note"]
            row_tab = ["A", "B", "C", "D"]
            i = 0
            for header in header_tab:
                cell = row_tab[i]+str(line)
                worksheet_ost.write(cell, header, cell_header)
                i += 1

            # FILL SHEET CONTENT
            line = 13
            for note_list in note_id.note_list_ids:
                cell = "A"+str(line)
                worksheet_ost.write(cell, note_list.audit or '', cell_11_left)
                cell = "B"+str(line)
                worksheet_ost.write(cell, note_list.student_name or '', cell_11_left)
                cell = "C"+str(line)
                worksheet_ost.write(cell, note_list.student_first_name or '', cell_11_left)
                cell = "D"+str(line)
                worksheet_ost.write(cell, note_list.note_sem1 or note_list.note_sem2 or '', cell_11_left)
                line += 1

            # Italic
            foot1 = "* note finale sur 20. En cas d'absence de note, merci de ne pas utiliser de chiffre "
            cell = "A"+str(line)+":D"+str(line)
            worksheet_ost.merge_range(cell, foot1, left_8_italic)
            line += 1

            # Date
            dt = date.today()
            cell = "A"+str(line)+":D"+str(line)
            worksheet_ost.merge_range(cell, "Date : "+datetime.strftime(dt, "%d/%m/%Y"), left_10)
            line += 2

            # Nom de l'enseignant
            cell = "A"+str(line)+":D"+str(line)
            worksheet_ost.merge_range(cell, "Nom de l'enseignant :", left_10)

    def style(self, worksheet):
        worksheet.set_column('A:A', 13)
        worksheet.set_column('B:B', 27)
        worksheet.set_column('C:C', 27)
        worksheet.set_column('D:D', 18)
        for i in range(6, 300):
            worksheet.set_row(i, 23)