# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date

class RecapEngagement(http.Controller):

    @http.route('/web/binary/download_recap_engagement_xls_file', auth='public')
    def  download_recap_engagement(self, school_year = False, str_insc = False):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        inscription_ids = False
        if str_insc and str_insc != 'False':
            insc_tab = [int(x) for x in str_insc.split('-')]
            inscription_ids = request.env['inscription.edu'].sudo().search([('id', 'in', insc_tab)])

        school_year_id = request.env['school.year'].browse(int(school_year)) if school_year and school_year != 'False' else False

        self.report_excel_recap_engagement(workbook, school_year_id, inscription_ids)  
        workbook.close()
        output.seek(0)

        if school_year_id:
            file_name = "Creance_"+school_year_id.name+"_arreté_du"+str(date.today())+".xlsx"
        else:
            file_name = "Creance_arreté_du"+str(date.today())+".xlsx"

        xlsheader = [('Content-Type', 'application/octet-stream'),
                     ('Content-Disposition', 'attachment; filename=%s;' % file_name)]
        return request.make_response(output, xlsheader)

    def report_excel_recap_engagement(self, workbook, school_year_id, inscription_ids = False):
        center_bold_12 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
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
        cell_bold_right_12 = workbook.add_format({
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
            "font_size": 12,
            "bold": True,
            })

        cell_center_grey_12 = workbook.add_format({
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
            "bg_color": '#a6a6a6',
            })
        cell_bold_right_grey_12 = workbook.add_format({
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
            "font_size": 12,
            "bold": True,
            "bg_color": '#a6a6a6',
            })
        cell_right_red_bold_12 = workbook.add_format({
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
            "font_size": 12,
            "bg_color": '#ff0000',
            "bold": True,
            })
        cell_right_12 = workbook.add_format({
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
            "font_size": 12,
            })

        row_tab = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ',
            'BA', 'BB', 'BC', 'BD', 'BE', 'BF', 'BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'BN', 'BO', 'BP', 'BQ', 'BR', 'BS', 'BT', 'BU', 'BV', 'BW', 'BX', 'BY', 'BZ',
            'CA', 'CB', 'CC', 'CD', 'CE', 'CF', 'CG', 'CH', 'CI', 'CJ', 'CK', 'CL', 'CM', 'CN', 'CO', 'CP', 'CQ',
            'CR', 'CS', 'CT', 'CU', 'CV', 'CW', 'CX', 'CY', 'CZ', 'DA', 'DB', 'DC', 'DD', 'DE', 'DF', 'DG', 'DH', 'DI']


        currency = ['Creance Ariary', 'Creance Euro']

        domain_filter = [('staggering_ok', '=', True)]

        school_year_ids = school_year_id
        if not school_year_id:
            if not inscription_ids:
                school_year_ids = request.env['school.year'].search([])
            else:
                school_year_ids = inscription_ids.mapped('school_year')
                domain_filter += [('id', 'in', inscription_ids.ids)]

        domain_filter += [('school_year', 'in', school_year_ids.ids)]

        all_creance = request.env['inscription.edu'].search(domain_filter)
        ariary_ech = all_creance.filtered(lambda insc: insc.amount_total_ariary > 0)
        devise_ech = all_creance.filtered(lambda insc: insc.amount_total_euro > 0)

        currency_ariary = request.env.ref('base.MGA')
        currency_euro = request.env.ref('base.EUR')

        for creance in currency:
            worksheet_ost = workbook.add_worksheet(creance)
            self.style(worksheet_ost)
            line = 2
            for school_year_id in school_year_ids:
                worksheet_ost.write("A"+str(line), "N° Engagement", cell_bold_center_12)
                worksheet_ost.write("B"+str(line), "NOM", cell_bold_center_12)
                worksheet_ost.write("C"+str(line), "Montant Total", cell_bold_center_12)
                worksheet_ost.write("D"+str(line), "Paiements", cell_bold_right_12)
                worksheet_ost.write("E"+str(line), "Reste à Payer", cell_bold_right_12)

                i = 0
                for row in row_tab:
                    cell = row+str(line+1)
                    if i == 1:
                        worksheet_ost.write(cell, 'Année Universitaire: '+school_year_id.name if school_year_id else 'TOUT', cell_center_grey_12)
                        i += 1
                        continue

                    worksheet_ost.write(cell, '', cell_center_grey_12)
                    i += 1

                echelo = ariary_ech if creance == 'Creance Ariary' else devise_ech
                echelo = echelo.filtered(lambda x: x.school_year == school_year_id)

                col = 5
                temp = 0
                for val in range(0,18):
                    month_year = self.get_month_year(school_year_id, temp)

                    col_init = col

                    cell = row_tab[col]+str(line)
                    worksheet_ost.write(cell, 'Date', cell_bold_right_grey_12)

                    col+=1
                    cell = row_tab[col]+str(line)
                    worksheet_ost.write(cell, 'Montant', cell_bold_right_grey_12)

                    col += 1
                    cell = row_tab[col]+str(line)
                    worksheet_ost.write(cell, 'Date', cell_bold_right_12)

                    col +=1
                    cell = row_tab[col]+str(line)
                    worksheet_ost.write(cell, 'N° Reçu', cell_bold_right_12)

                    col += 1
                    cell = row_tab[col]+str(line)
                    worksheet_ost.write(cell, 'DEJA PAYE', cell_right_red_bold_12)

                    # New column Report
                    col += 1
                    cell = row_tab[col]+str(line)
                    worksheet_ost.write(cell, "Report", cell_bold_right_12)

                    col_last = col
                    cell = row_tab[col_init]+str(line-1)+':'+row_tab[col_last]+str(line-1)
                    worksheet_ost.merge_range(cell, month_year, cell_bold_center_12)

                    col += 1
                    temp += 1

                line += 2

                for insc in echelo:
                    cell = "A"+str(line)
                    worksheet_ost.write(cell, insc.num_engagement, cell_center_12)

                    cell = "B"+str(line)
                    worksheet_ost.write(cell, insc.display_name, cell_center_12)

                    # Amount Total
                    cell = "C"+str(line)
                    if creance == 'Creance Ariary':
                        amount_total = insc.amount_total_ariary
                    else:
                        amount_total = insc.amount_total_euro
                    amount_total = round(amount_total, 2)
                    worksheet_ost.write(cell, '{:,.2f}' .format(amount_total), cell_center_12)

                    # Amount Paid
                    cell = "D"+str(line)
                    if creance == "Creance Ariary":
                        currency_val = currency_ariary
                        paid = sum(l.cost_devise for l in insc.payment_inscription_ids.filtered(lambda p: p.currency_id == currency_ariary and p.state == 'paid'))
                    else:
                        currency_val = currency_euro
                        paid = sum(l.cost_devise for l in insc.payment_inscription_ids.filtered(lambda p: p.currency_id == currency_euro and p.state == 'paid'))
                    paid = round(paid, 2)
                    worksheet_ost.write(cell, '{:,.2f}' .format(paid) if paid else '-', cell_bold_right_12)

                    # Amount Remain to pay
                    cell = "E"+str(line)
                    if creance == 'Creance Ariary':
                        remain = insc.total_amount_du_ariary
                    else:
                        remain = insc.total_amount_du_euro
                    remain = round(remain, 2)
                    worksheet_ost.write(cell, '{:,.2f}' .format(remain) if remain else '-', cell_bold_right_12)

                    col = 4
                    temp = 6
                    for val in range(0,18):
                        date_from = self.get_date_from(school_year_id, temp)
                        date_to = self.get_date_to(school_year_id, temp)

                        payments = insc.payment_inscription_ids.filtered(lambda pay: pay.date < date_to and pay.date > date_from and pay.currency_id == currency_val)
                        payment = payments[0] if payments else False
                        
                        # Date Prevu
                        col += 1
                        cell = row_tab[col]+str(line)
                        worksheet_ost.write(cell, str(payment.date).replace('-', '/') if payment else '', cell_right_12)
                        
                        # Montant
                        col += 1
                        cell = row_tab[col]+str(line)
                        worksheet_ost.write(cell, '{:,.2f}' .format(round(payment.cost_devise, 2)) if payment else '', cell_right_12)
                        
                        # Date Payment
                        col += 1
                        cell = row_tab[col]+str(line)
                        worksheet_ost.write(cell, str(payment.report_date).replace('-','/') if (payment and payment.state == 'granted') else '', cell_right_12)
                        
                        # N° Reçu
                        col += 1
                        cell = row_tab[col]+str(line)
                        x_payment_ids = payment.payment_ids if payment else False
                        # x_invoice_ids = x_payment_ids.mapped('invoice_ids').filtered(lambda x: x.state != 'draft') if x_payment_ids else False
                        x_rec_name = ''
                        if x_payment_ids:
                            for inv in x_payment_ids:
                                if inv.communication:
                                    x_rec_name += inv.communication if not x_rec_name else ', '+inv.communication
                        worksheet_ost.write(cell, x_rec_name, cell_right_12)

                        # DEJA PAYE
                        col += 1
                        cell = row_tab[col]+str(line)
                        worksheet_ost.write(cell, '{:,.2f}' .format(round(payment.cost_devise,2)) if payment and payment.payment_state == True else '', cell_right_12)
                        temp += 1

                        # Report
                        col += 1
                        cell = row_tab[col]+str(line)
                        report = ''
                        if payment:
                            if payment.state == 'request':
                                report = 'Report demandé'
                            elif payment.state == 'granted':
                                report = 'Report accordé'
                            elif payment.state == 'irrecouvrable':
                                report = 'Irrecouvrable'
                            elif  payment.state == 'paid':
                                report = 'Soldé'
                            elif  payment.state == 'non-paid':
                                report = 'Non Soldé'
                        worksheet_ost.write(cell, report, cell_right_12)

                    line += 1

                line += 3

        # Onglet Suivi
        worksheet_ost = workbook.add_worksheet("Suivi")
        self.style_suivi(worksheet_ost)
        cell_bold_center_11 = workbook.add_format({
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
        bold_center_11 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            "font_size": 11,
            "bold": True,
            })
        cell_left_11 = workbook.add_format({
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
            "font_size": 11,
            })
        cell_right_11 = workbook.add_format({
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
            "font_size": 11,
            })
        cell_right_grey_11 = workbook.add_format({
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
            "font_size": 11,
            "bg_color": '#a6a6a6',
            })

        header_tab = ["Noms et prénoms ", "Date prévue", "Montant", "Date de paiement", "Montant", "Déjà payer", 
                        "Reste à Payer", "Date de paiement du reste"]
        line = 1
        for creance in currency:
            cell = "A"+str(line)+":D"+str(line)
            val = "Reste Echéance Ariary" if creance == "Creance Ariary" else "Reste Echéance Euro"
            worksheet_ost.merge_range(cell, val, bold_center_11)
            line += 2
            i = 0
            for header in header_tab:
                cell = row_tab[i]+str(line)
                worksheet_ost.write(cell, header, cell_bold_center_11)
                i += 1

            x_total_remain = 0

            line += 1
            echeance = ariary_ech if creance == "Creance Ariary" else devise_ech
            for insc in echeance:
                cell = "A"+str(line)
                worksheet_ost.write(cell, insc.display_name, cell_left_11)

                cell = "B"+str(line)
                worksheet_ost.write(cell, '', cell_left_11)

                cell = "C"+str(line)
                amount = insc.amount_total_ariary if creance == "Creance Ariary" else insc.amount_total_euro
                worksheet_ost.write(cell, '{:,.2f}' .format(round(amount,2)), cell_right_11)

                cell = "D"+str(line)
                worksheet_ost.write(cell, '', cell_left_11)

                cell = "E"+str(line)
                worksheet_ost.write(cell, '', cell_left_11)

                currency_val = currency_ariary if creance == "Creance Ariary" else currency_euro

                cell = "F"+str(line)
                paid_amount = sum( l.cost_devise for l in insc.payment_inscription_ids.filtered(lambda pay: pay.currency_id == currency_val))
                worksheet_ost.write(cell, '{:,.2f}' .format(round(paid_amount,2)), cell_right_11)

                cell = "G"+str(line)
                remain = insc.total_amount_du_ariary if creance == "Creance Ariary" else insc.total_amount_du_euro
                x_total_remain += remain
                worksheet_ost.write(cell, '{:,.2f}' .format(round(remain,2)),cell_right_11)

                cell = "H"+str(line)
                worksheet_ost.write(cell, '', cell_left_11)
                line += 1

            cell = "G"+str(line)
            worksheet_ost.write(cell, '{:,.2f}' .format(round(x_total_remain,2)), cell_right_grey_11)
            line += 3





    def style(self, worksheet):
        worksheet.set_column('A:A', 16)
        worksheet.set_column('B:B', 55)
        worksheet.set_column('C:DI', 20)
        worksheet.set_row(1, 20)

    def style_suivi(self, worksheet):
        worksheet.set_column('A:A', 32)
        worksheet.set_column('B:C', 17)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:F', 17)
        worksheet.set_column('G:G', 18)
        worksheet.set_column('F:F', 23)
        worksheet.set_column('H:H', 25)

    def get_date_from(self, school_year, nb):
        if nb > 12:
            nb = nb -12
            year = int(school_year.name.split('-')[1])
        else:
            year = int(school_year.name.split('-')[0])
        return date(year, nb, 1)


    def get_date_to(self, school_year, nb):
        month_31 = [1, 3, 5, 7, 8, 10, 12]
        if nb > 12:
            nb = nb -12
            year = int(school_year.name.split('-')[1])
        else:
            year = int(school_year.name.split('-')[0])

        if nb in month_31:
            max_day = 31
        elif nb == 2:
            max_day = 28
        else:
            max_day = 30
        return date(year, nb, max_day)


    def get_month_year(self, school_year, nb):
        month_tab = ['Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.', 'Déc.', 'Janv.', 'Fév.', 
                    'Mars', 'Avril', 'Mei', 'Juin', 'Juil.', 'Août', 'Sept.', 'Oct.', 'Nov.']
        if nb < 7:
            year = school_year.name.split('-')[0]
        else:
            year = school_year.name.split('-')[1]

        month_year = month_tab[nb]+year
        return month_year