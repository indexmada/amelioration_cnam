# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date

class TutorServiceController(http.Controller):

    @http.route('/web/binary/download_report_payroll_xlsx', auth='public')
    def download_report_payroll_xlsx(self, str_id=False, element='acc'):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        id_tab = [int(x) for x in str_id.split('-')]
        domain = [('id', 'in', id_tab)]
        tutor_service_ids = request.env['tutor.service'].sudo().search(domain)
        self.report_excel_payroll(workbook, tutor_service_ids, element)  
        workbook.close()
        output.seek(0)

        file_name = "Etat_de_paie_tuteur.xlsx"

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)

    def report_excel_payroll(self, workbook, service_ids, element = 'acc'):
        center_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 11,
            })

        left_11 = workbook.add_format({
            'align': 'left',
            'valign': 'vleft',
            "font_size": 11,
            })

        left_11_italic = workbook.add_format({
            'align': 'left',
            'valign': 'vleft',
            "font_size": 11,
            "italic": True,
            })

        center_11_bold = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 11,
            "bold": True,
            })

        cell_center_11_bold = workbook.add_format({
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
        cell_right_11_bold = workbook.add_format({
            'align': 'right',
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

        dg_cell_center_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'right_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            })
        cell_tot_1 = workbook.add_format({
            'align': 'right',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'right_color': 'black',
            'left_color': 'black',
            "font_size": 11,
            })

        count = 1
        tutor_displayed = []
        for service_id in service_ids:
            if service_id.tutor_id.id in tutor_displayed:
                continue
            tutor_displayed.append(service_id.tutor_id.id)

            worksheet_ost = workbook.add_worksheet("feuille"+str(count))
            self.payroll_style(worksheet_ost)
            count += 1

            logo_image = io.BytesIO(base64.b64decode(request.env.company.logo))
            worksheet_ost.insert_image('A1', "image.png", {'image_data': logo_image,'x_scale': 0.50,'y_scale':0.50})
            worksheet_ost.merge_range("A5:B5", "CENTRE  Cnam Madagascar", center_11)
            worksheet_ost.merge_range("A6:B6", "Maison des Produits 67 Ha – 6ème Etage", center_11)
            worksheet_ost.merge_range("A7:B7", "Antananarivo 101", center_11)
            worksheet_ost.merge_range("A8:B8", "Madagascar", center_11)
            worksheet_ost.merge_range("A9:B9", "--------------------------------", center_11)
            worksheet_ost.merge_range("A10:B10", "Tèl. 261 38 22 290 19", center_11)
            worksheet_ost.merge_range("A11:B11", "E-mail: cnam.madagascar@yahoo.com", center_11)

            worksheet_ost.write("C13", "ETAT DE PAIEMENT", center_11_bold)
            worksheet_ost.write("C14", "Indemnité: 2023 - 2024", center_11_bold)

            worksheet_ost.write("A16", "NOM", cell_center_11_bold)
            worksheet_ost.write("B16", "FONCTION", cell_center_11_bold)
            worksheet_ost.write("C16", "LIBELLE", cell_center_11_bold)
            worksheet_ost.write("D16", "Montant (Ar)", cell_center_11_bold)
            worksheet_ost.write("E16", "EMARGEMENT", cell_center_11_bold)

            worksheet_ost.write("A17", "", dg_cell_center_11)
            worksheet_ost.write("B17", "", dg_cell_center_11)
            worksheet_ost.write("C17", "", dg_cell_center_11)
            worksheet_ost.write("D17", "", dg_cell_center_11)
            worksheet_ost.write("E17", "", dg_cell_center_11)

            worksheet_ost.write("A18", "Monsieur", dg_cell_center_11)
            worksheet_ost.write("B18", "Professeur", dg_cell_center_11)
            worksheet_ost.write("C18", "Honoraire", dg_cell_center_11)
            amount = 0
            for service in service_ids.filtered(lambda serv: serv.tutor_id == service_id.tutor_id):
                if element == 'reste':
                    amount += service.amount_residual
                elif element == 'total':
                    amount += service.amount
                else:
                    amount += service.amount_deposit
                service_ids -= service
            worksheet_ost.write("D18", '{:,.2f}' .format(amount), cell_tot_1)
            worksheet_ost.write("E18", "", dg_cell_center_11)

            worksheet_ost.write("A19", service_id.tutor_id.name, dg_cell_center_11)
            worksheet_ost.write("B19", "", dg_cell_center_11)
            worksheet_ost.write("C19", service_id.semestre_id.name, dg_cell_center_11)
            worksheet_ost.write("D19", "", cell_tot_1)
            worksheet_ost.write("E19", "", dg_cell_center_11)

            worksheet_ost.write("A20", "", dg_cell_center_11)
            worksheet_ost.write("B20", "", dg_cell_center_11)
            worksheet_ost.write("C20", "", dg_cell_center_11)
            worksheet_ost.write("D20", "", dg_cell_center_11)
            worksheet_ost.write("E20", "", dg_cell_center_11)

            worksheet_ost.write("A21", "", dg_cell_center_11)
            worksheet_ost.write("B21", "", dg_cell_center_11)
            worksheet_ost.write("C21", "", dg_cell_center_11)
            worksheet_ost.write("D21", "", dg_cell_center_11)
            worksheet_ost.write("E21", "", dg_cell_center_11)

            # TOTAL LINE
            worksheet_ost.write("A22", "TOTAL", cell_center_11_bold)
            worksheet_ost.write("B22", "", cell_center_11_bold)
            worksheet_ost.write("C22", "", cell_center_11_bold)
            worksheet_ost.write("D22", '{:,.2f}' .format(amount), cell_right_11_bold)
            worksheet_ost.write("E22", "", cell_center_11_bold)

            currency_ariary = request.env.ref('base.MGA')

            worksheet_ost.write("A25", "Arrêté le présent état à la somme de: "+ currency_ariary.amount_to_text(amount), left_11)
            worksheet_ost.write("D27", "Antananarivo,", left_11_italic)

            worksheet_ost.write("D30", "Le Directeur",center_11)
            worksheet_ost.write("D35", "Jocelyn RASOANAIVO", center_11)

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
            worksheet_ost.write("A1", "RECAP "+semester_id.name+" "+semester_id.school_year_id.name, left_bold_11)

            line = 3
            header_tab = ["Semestre", "UE", "Debut", "Fin cours", "Nb heures", "Taux Horaire", "Taux accompte", "Heure Passer", 
                            "M.à payer", "Acc Fin", "Payé", "Date Paiement", "Reste à Payer"]

            row_tab = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
            tutor_service_ids = request.env['tutor.service'].sudo().search([('semestre_id', '=', semester_id.id)])
            tutor_ids = tutor_service_ids.mapped('tutor_id')
            for tutor_id in tutor_ids:
                i = 0
                service_ids = tutor_service_ids.filtered(lambda x: x.tutor_id == tutor_id)
                intec = service_ids[0].org_select == 'intec'
                for header in header_tab:
                    if service_ids and service_ids[0].org_select == 'intec':
                        if header in ['Taux accompte', 'Acc Fin', 'Payé', 'Reste à Payer']:
                            continue
                    cell_style = cell_center_bold_11_yellow if header == "Payé" else cell_center_bold_11
                    worksheet_ost.write(row_tab[i]+str(line), header, cell_style)
                    i += 1

                line += 1
                cell = "A"+str(line)+":M"+str(line)
                worksheet_ost.merge_range(cell, tutor_id.name, cell_center_11_green)

                line += 1
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
                    worksheet_ost.write("C"+str(line), service.date_begin.strftime("%d/%m/%Y") if service.date_begin else '', cell_center_11)
                    worksheet_ost.write("D"+str(line), service.date_end.strftime("%d/%m/%Y") if service.date_begin else '', cell_center_11)

                    nb_hours = '{0:02.0f}h{1:02.0f}'.format(*divmod(float(service.nb_hours) * 60, 60))
                    worksheet_ost.write("E"+str(line), nb_hours, cell_center_11)
                    worksheet_ost.write("F"+str(line), '{:,.2f}' .format(service.hourly_rate), cell_center_11)
                    i = 6
                    if not intec:
                        worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(service.rate_deposit), cell_center_11)
                        i+= 1
                    worksheet_ost.write(row_tab[i]+str(line), service.nb_hours_passed, cell_center_11)
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(service.amount), cell_center_11)
                    i += 1

                    # Acc Fin
                    acc_fin = 0
                    if not intec:
                        acc_fin = service.nb_hours_passed * service.hourly_rate
                        worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(acc_fin), cell_center_11)
                        i += 1
                        worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(acc_fin), cell_center_11)
                        i += 1
                    worksheet_ost.write(row_tab[i]+str(line), '', cell_center_11)
                    i += 1

                    remain_to_pay = 0
                    if not intec:
                        remain_to_pay = service.amount - acc_fin
                        worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(remain_to_pay), cell_center_11)
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
                worksheet_ost.write("F"+str(line), '{:,.2f}' .format(total_hourly_rate), cell_center_bold_11_italic)
                i = 6
                if not intec:
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_rate_deposit), cell_center_bold_11_italic)
                    i += 1
                worksheet_ost.write(row_tab[i]+str(line), total_nb_hours_passed, cell_center_bold_11_italic)
                i += 1

                worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_service_amount), cell_center_bold_11_italic)
                i += 1
                if not intec:
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_acc_fin), cell_center_bold_11_italic)
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_acc_fin), cell_center_bold_11_yellow)
                    i += 1
                worksheet_ost.write(row_tab[i]+str(line), '', cell_center_bold_11_italic)
                i += 1
                if not intec:
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_remain_to_pay), cell_center_bold_11_italic)
                    i += 1

                # Total Général
                line += 1
                i = 0
                worksheet_ost.merge_range("A"+str(line)+":D"+str(line+1), "TOTAL GENERAL", cell_center_bold_11_grey)
                cell_style = cell_center_bold_11_grey
                for header in header_tab:
                    if intec and header in ['Taux accompte', 'Acc Fin', 'Payé', 'Reste à Payer']: 
                        continue
                        ["Semestre", "UE", "Debut", "Fin cours", "Nb heures", "Taux Horaire", "Taux accompte", "Heure Passer", 
                            "M.à payer", "Acc Fin", "Payé", "Date Paiement", "Reste à Payer"]
                    if header in ['Nb heures', 'Heure Passer', 'M.à payer', 'Acc Fin', 'Acc Fin', "Reste à Payer"]:
                        worksheet_ost.write(row_tab[i]+str(line), header, cell_style)
                    elif i in ['Taux Horaire', 'Taux accompte', 'Date Paiement']:
                        worksheet_ost.write(row_tab[i]+str(line), '', cell_style)
                line += 1
                worksheet_ost.write("E"+str(line), total_nb_hours, cell_center_bold_11_grey)
                worksheet_ost.write("F"+str(line), '', cell_center_bold_11_grey)
                i = 6
                if not intec:
                    worksheet_ost.write(row_tab[i]+str(line), '', cell_center_bold_11_grey)
                    i += 1
                worksheet_ost.write(row_tab[i]+str(line), total_nb_hours_passed, cell_center_bold_11_grey)
                i += 1
                worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_service_amount), cell_center_bold_11_yellow if intec else cell_center_bold_11_grey)
                i += 1
                if not intec:
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_acc_fin), cell_center_bold_11_yellow)
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_acc_fin), cell_center_bold_11_yellow)
                    i += 1
                worksheet_ost.write(row_tab[i]+str(line), '', cell_center_bold_11_grey)
                i += 1
                if not intec:
                    worksheet_ost.write(row_tab[i]+str(line), '{:,.2f}' .format(total_remain_to_pay), cell_center_bold_11_grey)
                    i += 1
                if not intec:
                    worksheet_ost.write("J"+str(line+1), "Montant à payer", cell_center_bold_11_yellow)
                    worksheet_ost.write("J"+str(line+2), semester_id.name, cell_center_bold_11_yellow)
                else:
                    worksheet_ost.write("H"+str(line+1), "Montant à payer", cell_center_bold_11_yellow)
                    worksheet_ost.write("H"+str(line+2), semester_id.name, cell_center_bold_11_yellow)
                line += 5

    def style(self, worksheet):
        worksheet.set_column('A:D', 12)
        worksheet.set_column("E:E", 10)
        worksheet.set_column("F:F", 12)
        worksheet.set_column("G:G", 14)
        worksheet.set_column("H:H", 16)
        worksheet.set_column("I:I", 14)
        worksheet.set_column("J:J", 16)
        worksheet.set_column("K:M", 14)
        worksheet.set_column("N:N", 12)

    def payroll_style(self, worksheet):
        worksheet.set_column("A:A", 48)
        worksheet.set_column("B:C", 28)
        worksheet.set_column("D:E", 19)
