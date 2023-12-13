# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date

DAY_WEEKS = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

class ResTutorController(http.Controller):

    @http.route('/web/binary/download_res_tutor_xls_file', auth='public')
    def  download_res_tutor(self, str_tutor = False):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        tutor_tab = [int(x) for x in str_tutor.split('-')]
        tutor_ids = request.env['res.tutor'].sudo().search([('id', 'in', tutor_tab)])
        self.report_excel_res_tutor(workbook, tutor_ids)  
        workbook.close()
        output.seek(0)

        file_name = "Pointage_Tuteur.xlsx"

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)

    def report_excel_res_tutor(self, workbook, tutor_ids):
        left_bold_11 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            "font_size": 11,
            "bold": True,
            })

        left_11 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            "font_size": 11,
            })

        cell_center_11 = workbook.add_format({
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
            })

        cell_center_bold_11 = workbook.add_format({
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
        header_tab = ["Jour", "Date", "Horaire", "Total"]
        row_tab = ["A", "B", "C", "D"]
        for tutor_id in tutor_ids:
            sheet_name = str(tutor_id.id)+"-"+tutor_id.name
            worksheet_ost = workbook.add_worksheet(sheet_name)
            self.style(worksheet_ost)
            logo_image = io.BytesIO(base64.b64decode(request.env.company.logo))
            worksheet_ost.insert_image('A1', "image.png", {'image_data': logo_image,'x_scale': 0.45,'y_scale':0.45})

            line = 4
            worksheet_ost.write('A'+str(line), "Tuteur : "+ tutor_id.name, left_11)

            regrouping_center_line_ids = request.env['regrouping.center.line'].sudo().search([]).filtered(lambda x: tutor_id in x.tutor_attendance)
            
            ue_config_ids = regrouping_center_line_ids.mapped('ue_config_id')

            line += 1
            for ue in ue_config_ids:
                worksheet_ost.write('A'+str(line), ue.code+" : "+ue.name, left_bold_11)
                line += 2

                # Header
                i = 0
                for header in header_tab:
                    worksheet_ost.write(row_tab[i]+str(line), header, cell_center_bold_11)
                    i += 1

                line += 1

                line_ids = regrouping_center_line_ids.filtered(lambda l: l.ue_config_id == ue)
                total_duration = 0
                for line_id in line_ids:
                    d = line_id.grouping_date
                    wd = DAY_WEEKS[d.weekday()] if d else False
                    begin_hours = '{0:02.0f}h{1:02.0f}'.format(*divmod(float(line_id.begin_hours) * 60, 60))
                    end_hours = '{0:02.0f}h{1:02.0f}'.format(*divmod(float(line_id.end_hours) * 60, 60))
                    hour = begin_hours +"-"+end_hours

                    worksheet_ost.write("A"+str(line), wd, cell_center_11)
                    worksheet_ost.write("B"+str(line), d.strftime("%d/%m/%Y"), cell_center_11)
                    worksheet_ost.write("C"+str(line), hour, cell_center_11)
                    duration = '{0:02.0f}h{1:02.0f}'.format(*divmod(float(line_id.duration) * 60, 60))
                    worksheet_ost.write("D"+str(line), duration, cell_center_11)
                    total_duration += line_id.duration
                    line += 1
                cell = "A"+str(line)+":C"+str(line)
                worksheet_ost.merge_range(cell, "TOTAL", cell_center_bold_11)
                worksheet_ost.write("D"+str(line), '{0:02.0f}h{1:02.0f}'.format(*divmod(float(total_duration) * 60, 60)), cell_center_bold_11)

                line += 2

    def style(self, worksheet):
        worksheet.set_column('A:E', 13)