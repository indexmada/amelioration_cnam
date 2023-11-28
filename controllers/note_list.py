# -*- coding: utf-8 -*-

import base64
import xlsxwriter as xlsxwriter

from odoo import http
from odoo.http import request

import io
from ast import literal_eval

from datetime import date

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