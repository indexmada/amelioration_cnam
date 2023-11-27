# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date,datetime

class RecapEngagement(http.Controller):

    @http.route('/web/binary/download_insc_recap_xls_file', auth='public')
    def  download_insc_recap(self, str_school_year_ids, str_date_from = False, str_date_to = False):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)

        if str_school_year_ids not in ['0', 0]:
            school_year_tab = str_school_year_ids.split("-")
            school_year_tab.pop()
            res = [eval(i) for i in school_year_tab]
            school_year_ids = request.env["school.year"].sudo().search([('id', 'in', res)])

        else:
            school_year_ids = request.env["school.year"].sudo().search([])

        date_from = datetime.strptime(str_date_from, "%d-%m-%Y").date() if str_date_from else False
        date_to = datetime.strptime(str_date_to, "%d-%m-%Y").date() if str_date_to else False


        self.report_excel_insc_recap(workbook, school_year_ids, date_from, date_to)
        workbook.close()
        output.seek(0)

        file_name = "Listes Récapitulatives Inscription"+".xlsx"

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)

    def report_excel_insc_recap(self, workbook, school_year_ids, date_from = False, date_to= False):
        center_10 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 10,
            "bold": False,
            })
        right_10 = workbook.add_format({
            'align': 'right',
            'valign': 'vright',
            "font_size": 10,
            "bold": False,
            })
        center_10_bold = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 10,
            "bold": True,
            })
        cell_center_10_bold = workbook.add_format({
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
            "font_size": 10,
            "bold": True,
            })

        cell_center_10 = workbook.add_format({
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
            "font_size": 10,
            })

        cell_left_10 = workbook.add_format({
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
            "font_size": 10,
            })

        cell_right_10 = workbook.add_format({
            'align': 'right',
            'valign': 'vright',
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'right_color': 'black',
            'bottom_color': 'black',
            'top_color': 'black',
            'left_color': 'black',
            "font_size": 10,
            })

        header_tab = ["N° Ordre", "Date", "N° reçu", "N° Auditeur", "Nom", "Prénoms", "Filière", "Formation"]

        row_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ',
            'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ',
            'CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ', 'CR', 'CS', 'CT', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ']

        for year in school_year_ids:
            worksheet_ost = workbook.add_worksheet(year.name)
            self.style(worksheet_ost)

            domain = [('school_year', '=', year.id), ('inscription_date', '!=', False)]
            if date_from:
                domain += [('inscription_date', '>=', date_from)]
            if date_to:
                domain += [('inscription_date', '<=', date_to)]

            insc_ids = request.env["inscription.edu"].search(domain, order="inscription_date")
            insc_dates = insc_ids.mapped("inscription_date")
            line = 6
            insc_dates = self.remove_duplicate_date(insc_dates)
            for insc_date in insc_dates:
                worksheet_ost.merge_range("E"+str(line)+":G"+str(line), "RECAPITULATIF DES INSCRIPTIONS "+str(year.name), center_10)
                line += 1
                worksheet_ost.merge_range("E"+str(line)+":G"+str(line), "Arrêté le: "+datetime.strftime(insc_date, "%d/%m/%Y"), center_10_bold)
                line += 1
                # Numéro records en colonne
                line += 1
                i = 0
                for header in header_tab:
                    worksheet_ost.merge_range(row_tab[i]+str(line)+":"+row_tab[i]+str(line + 2), header, cell_center_10_bold)
                    i += 1

                insc_res_ids = insc_ids.filtered(lambda x: x.inscription_date == insc_date)
                max_length = max(len(x.units_enseignes + x.other_ue_ids) for x in insc_res_ids)

                # Fill UE header
                j = 0
                for ue in range(0, max_length+3):
                    val = "UE" if j < max_length else "DIB" if j<max_length+1 else "FD" if j<max_length+2 else "FC"
                    worksheet_ost.merge_range(row_tab[i]+str(line)+":"+row_tab[i+2]+str(line), val, cell_center_10_bold)
                    worksheet_ost.merge_range(row_tab[i]+str(line+1)+":"+row_tab[i]+str(line+2), "Code", cell_center_10_bold)
                    worksheet_ost.merge_range(row_tab[i+1]+str(line+1)+":"+row_tab[i+2]+str(line+1), "Montant", cell_center_10_bold)
                    worksheet_ost.write(row_tab[i+1]+str(line+2), "Ariary", cell_center_10_bold)
                    worksheet_ost.write(row_tab[i+2]+str(line+2), "Euro", cell_center_10_bold)
                    i += 3
                    j += 1

                # TOTAL GENERAL HEADER
                worksheet_ost.merge_range(row_tab[i]+str(line+1)+":"+row_tab[i+1]+str(line+1), "TOTAL GENERAL", cell_center_10_bold)
                worksheet_ost.write(row_tab[i]+str(line+2), "Ariary", cell_center_10_bold)
                worksheet_ost.write(row_tab[i+1]+str(line+2), "Euro", cell_center_10_bold)
                i += 2

                # TOTAL UE HEADER
                worksheet_ost.merge_range(row_tab[i]+str(line+1)+":"+row_tab[i]+str(line+2), "TOTAL UE", cell_center_10_bold)

                count = 0
                line += 3

                x_total_mga = 0
                x_total_currency = 0
                for insc in insc_res_ids:
                    total_mga = 0
                    total_currency = 0
                    i = 0
                    count += 1
                    # N° Ordre
                    worksheet_ost.write(row_tab[i]+str(line), str(insc.id), cell_center_10)

                    # Date
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), datetime.strftime(insc.inscription_date, "%d/%m/%Y"), cell_center_10)

                    # N° Reçu
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), insc.insc_ref_recu or '', cell_left_10)

                    # N° Auditeur
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), insc.name or '', cell_left_10)

                    # Nom
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), insc.surname or '', cell_left_10)

                    # Prénoms
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), insc.firstname or '', cell_left_10)

                    # Filière
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), insc.faculty_id.name if insc.faculty_id else '', cell_left_10)

                    # Formation
                    i += 1
                    worksheet_ost.write(row_tab[i]+str(line), insc.formation_id.name if insc.formation_id else '', cell_left_10)

                    # Lister Details UE
                    i += 1
                    for ue in (insc.units_enseignes + insc.other_ue_ids):
                        worksheet_ost.write(row_tab[i]+str(line), ue.name.code, cell_left_10)
                        if ue.currency_id.name == "MGA":
                            worksheet_ost.write(row_tab[i+1]+str(line), '{:,}' .format(round(ue.cost_ariary, 2)), cell_right_10)
                            worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)
                            total_mga += ue.cost_ariary
                        else:
                            worksheet_ost.write(row_tab[i+1]+str(line), '', cell_right_10)
                            worksheet_ost.write(row_tab[i+2]+str(line), '{:,}' .format(round(ue.cost_devise, 2)), cell_right_10)
                            total_currency += ue.cost_devise
                        i += 3

                    # DIB
                    if insc.dib:
                        worksheet_ost.write(row_tab[i]+str(line), "DIB", cell_left_10)
                        if insc.dib_currency_id.name == "MGA":
                            worksheet_ost.write(row_tab[i+1]+str(line), '{:,}' .format(round(insc.amount_dib, 2)), cell_right_10)
                            worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)
                        else:
                            worksheet_ost.write(row_tab[i+1]+str(line), '', cell_right_10)
                            worksheet_ost.write(row_tab[i+2]+str(line), '{:,}' .format(round(insc.amount_dib, 2)), cell_right_10)

                    else: 
                        worksheet_ost.write(row_tab[i]+str(line), "", cell_left_10)
                        worksheet_ost.write(row_tab[i+1]+str(line), '', cell_right_10)
                        worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)

                    i += 3
                    # FD & FC
                    worksheet_ost.write(row_tab[i]+str(line), "", cell_left_10)
                    worksheet_ost.write(row_tab[i+1]+str(line), '', cell_right_10)
                    worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)
                    i += 3

                    worksheet_ost.write(row_tab[i]+str(line), "", cell_left_10)
                    worksheet_ost.write(row_tab[i+1]+str(line), '', cell_right_10)
                    worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)
                    i += 3

                    # TOTAL GENERAL
                    worksheet_ost.write(row_tab[i]+str(line), '{:,}' .format(round(total_mga, 2)),cell_right_10)
                    worksheet_ost.write(row_tab[i+1]+str(line), '{:,}' .format(round(total_currency, 2)),cell_right_10)

                    # TOTAL UE
                    worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)
                    line += 1

                    # Total
                    x_total_mga += total_mga
                    x_total_currency += total_currency

                worksheet_ost.write(row_tab[i]+str(line), '{:,}' .format(round(x_total_mga, 2)), cell_right_10)
                worksheet_ost.write(row_tab[i+1]+str(line), '{:,}' .format(round(x_total_currency, 2)), cell_right_10)
                worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)

                line += 2
                # Total arrêté ce: jj/mm/AAAA
                worksheet_ost.write(row_tab[i-4]+str(line), "Total arrêté ce:", center_10)
                worksheet_ost.write(row_tab[i-3]+str(line), datetime.strftime(insc_date, "%d/%m/%Y"), right_10)
                worksheet_ost.write(row_tab[i]+str(line), '{:,}' .format(round(x_total_mga, 2)), cell_right_10)
                worksheet_ost.write(row_tab[i+1]+str(line), '{:,}' .format(round(x_total_currency, 2)), cell_right_10)
                worksheet_ost.write(row_tab[i+2]+str(line), '', cell_right_10)
                
                line += 2

    def style(self, worksheet):
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:C', 9)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:F', 20)
        worksheet.set_column('G:G', 7)
        worksheet.set_column('H:H', 16)
        worksheet.set_column('I:CZ', 11)
        # worksheet.set_row(1, 20)

    def remove_duplicate_date(self, date_tab): 
        res = []
        for d in date_tab:
            if d not in res:
                res.append(d)

        return res