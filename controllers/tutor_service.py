# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date

class TutorServiceController(http.Controller):

    @http.route('/web/binary/download_recap_honoraire_tuteur_xlsx', auth='public')
    def  download_recap_honoraire(self, str_semester = False):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        semester_tab = [int(x) for x in str_semester.split('-')] if str_semester and str_semester != 'False' else False
        domain = [('id', 'in', semester_tab)] if semester_tab else []
        semester_ids = request.env['semestre.edu'].sudo().search(domain)
        self.report_excel_recap_honoraire(workbook, semester_ids)  
        workbook.close()
        output.seek(0)

        file_name = "Honoraire_Tuteur.xlsx"

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)


    def report_excel_recap_honoraire(self, workbook, semester_ids):
        left_bold_11 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',
            "font_size": 11,
            "bold": True,
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
        cell_center_11_green = workbook.add_format({
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
            "bg_color": "#d7e4bd",
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
        cell_center_bold_11_grey = workbook.add_format({
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
            "bg_color": "#bfbfbf"
            })
        cell_center_bold_11_italic = workbook.add_format({
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
            "italic": True,
            })
        cell_center_bold_11_yellow = workbook.add_format({
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
            "bg_color": "#ffc000",
            })

        for semester_id in semester_ids:
            sheet_name = "Recap honoraire Tuteur "+semester_id.display_name
            worksheet_ost = workbook.add_worksheet(sheet_name)
            self.style(worksheet_ost)
            worksheet_ost.write("A1", "RECAP HONORAIRE TUTEUR"+semester_id.name+" "+semester_id.school_year_id.name, left_bold_11)

            line = 3
            header_tab = ["Semestre", "UE", "Debut", "Fin cours", "Nb heures", "Taux Horaire", "Taux accompte", "Heure Passer", 
                            "M.à payer", "Acc Fin", "Payé", "Date Paiement", "Reste à Payer"]

            row_tab = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
            tutor_service_ids = request.env['tutor.service'].sudo().search([('semestre_id', '=', semester_id.id)])
            tutor_ids = tutor_service_ids.mapped('tutor_id')
            for tutor_id in tutor_ids:
                i = 0
                for header in header_tab:
                    cell_style = cell_center_bold_11_yellow if header == "Payé" else cell_center_bold_11
                    worksheet_ost.write(row_tab[i]+str(line), header, cell_style)
                    i += 1

                line += 1
                cell = "A"+str(line)+":M"+str(line)
                worksheet_ost.merge_range(cell, tutor_id.name, cell_center_11_green)

                line += 1
                service_ids = tutor_service_ids.filtered(lambda x: x.tutor_id == tutor_id)
                total_nb_hours = 0
                total_hourly_rate = 0
                total_rate_deposit = 0
                total_nb_hours_passed = 0
                total_service_amount = 0
                total_acc_fin = 0
                total_remain_to_pay = 0
                for service in service_ids:
                    worksheet_ost.write("A"+str(line), semester_id.name, cell_center_11)
                    worksheet_ost.write("B"+str(line), service.ue_config_id.code, cell_center_11)
                    worksheet_ost.write("C"+str(line), service.date_begin.strftime("%d/%m/%Y"), cell_center_11)
                    worksheet_ost.write("D"+str(line), service.date_end.strftime("%d/%m/%Y"), cell_center_11)

                    nb_hours = '{0:02.0f}h{1:02.0f}'.format(*divmod(float(service.nb_hours) * 60, 60))
                    worksheet_ost.write("E"+str(line), nb_hours, cell_center_11)
                    worksheet_ost.write("F"+str(line), '{:,}' .format(service.hourly_rate), cell_center_11)
                    worksheet_ost.write("G"+str(line), '{:,}' .format(service.rate_deposit), cell_center_11)
                    worksheet_ost.write("H"+str(line), service.nb_hours_passed, cell_center_11)
                    worksheet_ost.write("I"+str(line), '{:,}' .format(service.amount), cell_center_11)

                    # Acc Fin
                    acc_fin = service.nb_hours_passed * service.hourly_rate
                    worksheet_ost.write("J"+str(line), '{:,}' .format(acc_fin), cell_center_11)
                    worksheet_ost.write("K"+str(line), '{:,}' .format(acc_fin), cell_center_11)
                    worksheet_ost.write("L"+str(line), '', cell_center_11)

                    remain_to_pay = service.amount - acc_fin
                    worksheet_ost.write("M"+str(line), '{:,}' .format(remain_to_pay), cell_center_11)
                    total_nb_hours += service.nb_hours
                    total_hourly_rate += service.hourly_rate
                    total_rate_deposit += service.rate_deposit
                    total_nb_hours_passed += service.nb_hours_passed
                    total_service_amount += service.amount
                    total_acc_fin += acc_fin
                    total_remain_to_pay += remain_to_pay
                    line += 1

                # Total
                total_nb_hours = '{0:02.0f}h{1:02.0f}'.format(*divmod(float(total_nb_hours) * 60, 60))
                worksheet_ost.write("A"+str(line), "TOTAL", cell_center_bold_11_italic)
                worksheet_ost.write("B"+str(line), "", cell_center_bold_11_italic)
                worksheet_ost.write("C"+str(line), "", cell_center_bold_11_italic)
                worksheet_ost.write("D"+str(line), "", cell_center_bold_11_italic)
                worksheet_ost.write("E"+str(line), total_nb_hours, cell_center_bold_11_italic)
                worksheet_ost.write("F"+str(line), '{:,}' .format(total_hourly_rate), cell_center_bold_11_italic)
                worksheet_ost.write("G"+str(line), '{:,}' .format(total_rate_deposit), cell_center_bold_11_italic)
                worksheet_ost.write("H"+str(line), total_nb_hours_passed, cell_center_bold_11_italic)
                worksheet_ost.write("I"+str(line), '{:,}' .format(total_service_amount), cell_center_bold_11_italic)
                worksheet_ost.write("J"+str(line), '{:,}' .format(total_acc_fin), cell_center_bold_11_italic)
                worksheet_ost.write("K"+str(line), '{:,}' .format(total_acc_fin), cell_center_bold_11_yellow)
                worksheet_ost.write("L"+str(line), '', cell_center_bold_11_italic)
                worksheet_ost.write("M"+str(line), total_remain_to_pay, cell_center_bold_11_italic)

                # Total Général
                line += 1
                worksheet_ost.merge_range("A"+str(line)+":D"+str(line+1), "TOTAL GENERAL", cell_center_bold_11_grey)
                i = 0
                cell_style = cell_center_bold_11_grey
                for header in header_tab:
                    if i in [4, 7, 8, 9, 10, 12]:
                        worksheet_ost.write(row_tab[i]+str(line), header, cell_style)
                    elif i in [5, 6, 11]:
                        worksheet_ost.write(row_tab[i]+str(line), '', cell_style)
                    i += 1
                line += 1
                worksheet_ost.write("E"+str(line), total_nb_hours, cell_center_bold_11_grey)
                worksheet_ost.write("F"+str(line), '', cell_center_bold_11_grey)
                worksheet_ost.write("G"+str(line), '', cell_center_bold_11_grey)
                worksheet_ost.write("H"+str(line), total_nb_hours_passed, cell_center_bold_11_grey)
                worksheet_ost.write("I"+str(line), '{:,}' .format(total_service_amount), cell_center_bold_11_grey)
                worksheet_ost.write("J"+str(line), '{:,}' .format(total_acc_fin), cell_center_bold_11_yellow)
                worksheet_ost.write("K"+str(line), '{:,}' .format(total_acc_fin), cell_center_bold_11_yellow)
                worksheet_ost.write("L"+str(line), '', cell_center_bold_11_grey)
                worksheet_ost.write("M"+str(line), total_remain_to_pay, cell_center_bold_11_grey)

                worksheet_ost.write("J"+str(line+1), "Montant à payer", cell_center_bold_11_yellow)
                worksheet_ost.write("J"+str(line+2), semester_id.name, cell_center_bold_11_yellow)
                line += 5

    def style(self, worksheet):
        worksheet.set_column('A:D', 12)
        worksheet.set_column("E:E", 10)
        worksheet.set_column("F:F", 12)
        worksheet.set_column("G:G", 14)
        worksheet.set_column("H:H", 12)
        worksheet.set_column("I:I", 14)
        worksheet.set_column("J:J", 16)
        worksheet.set_column("K:M", 14)
        worksheet.set_column("N:N", 12)