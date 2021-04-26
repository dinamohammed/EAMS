# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import io
import base64

class ReportXlsxBudgetSix(models.AbstractModel):
    _name = 'report.budget_purchase_relation.report_bab_six_doc'
    _inherit = 'report.report_xlsx.abstract'
    
    
    def generate_xlsx_report(self, workbook, data, budgets):
        report_name = "ختامي الباب السادس"
        # One sheet by partner
        worksheet = workbook.add_worksheet(report_name[:31])
        format_left_to_right = workbook.add_format()
        format_left_to_right.set_reading_order(1)

        format_right_to_left = workbook.add_format()
        format_right_to_left.set_reading_order(2)
        cell_format_right = workbook.add_format()
        cell_format_right.set_align('right')

        
        worksheet.right_to_left()
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 30)
        worksheet.set_column('C:X', 15)
        bold = workbook.add_format({'bold': True})
        bold.set_font_size(13)
        bold_center = workbook.add_format({'bold': True, 'align': 'center'})
        bold_center.set_font_size(13)
        bold_right = workbook.add_format({'bold': True, 'align': 'right'})
        bold_right.set_font_size(13)
        bold_center_underline = workbook.add_format({'bold': True, 'align': 'right'})
        bold_center_underline.set_underline()
        
        bold_center.set_align('vcenter')
        
        bold_center_wrap = workbook.add_format({'bold': True, 'align': 'center'})
        bold_center_wrap.set_font_size(13)
        bold_center_wrap.set_text_wrap()
        
        worksheet.merge_range(0, 0, 0, 1, "وزارة الـنـقــل", bold_center_underline)
        worksheet.merge_range(1, 0, 1, 1, "قـطـاع الـنـقـل الـبـحــرى", bold_center_underline)
        worksheet.merge_range(2, 0, 2, 1, "الهـيـئـة المصـريـة لسـلامـة الـمـلاحـة الـبـحـريـــة", bold_center_underline)
        
        worksheet.merge_range(1, 2, 1, 12, "بـيـان المنـصـرف عـلـى الـبــاب الـسـادس - شـراء أصـول غـيـر مـالـيـــة ( إسـتـثـمـارات )", bold_center)
        worksheet.merge_range(2, 2, 2, 12, " مـوزعـاً عـلـى الـمـكـون الـعـيـنـي والـمـكـون الـنـقـدي  %s/%s"
                              %(fields.Date.today().year - 1,fields.Date.today().year), bold_center)
        
        
        bold_center_wrap.set_border()
        worksheet.merge_range(4, 0, 6, 1, "أســــــــــم الــمــشـــــــــــــروع", bold_center_wrap)
        worksheet.merge_range(4, 2, 6, 2, "اعـتـمـادات العـام المـالــي %s/%s المـعـدلــة"
                              %(fields.Date.today().year - 1,fields.Date.today().year), bold_center_wrap)
        worksheet.merge_range(4, 3, 6, 3, "المنــصـرف الـفـعـلـــي", bold_center_wrap)
        
#         worksheet.merge_range(4, 4, 5, 11, "الــمـــكـــون الــعــيـــنـــــي", bold_center_wrap)
        columns = []
        rows = []
        row = 6
        col = 4
        for idx, budget in enumerate(budgets):
            for line in budget.crossovered_budget_line:
                if line.analytic_account_id:
                    columns.append(line.analytic_account_id)
                if line.general_budget_id:
                    rows.append(line.general_budget_id)
                    
        columns = list(dict.fromkeys(columns))
        rows = list(dict.fromkeys(rows))
        for column in columns:
            worksheet.write(row, col, "%s" %column.name, bold_center_wrap)
            col += 1
            
        worksheet.merge_range(4, 4, 5, col, "الــمـــكـــون الــعــيـــنـــــي", bold_center_wrap)
#         col += 1
        worksheet.write(row, col, "الجملة", bold_center_wrap)
        col += 1
        worksheet.merge_range(4, col, 6, col, "جـمـلـــــة الــوفـــر / التــجــاوز", bold_center_wrap)
        
        row = 7
        col = 0
        for roww in rows:
            worksheet.merge_range(row, 0, row , 1, "%s" %roww.name, bold_center_wrap)
            row += 1
        
        col = 2
        for budget in budgets:
            sum_reserve = difference_reserve = 0
            for line in budget.crossovered_budget_line:
                if line.dependable_amount > 0:
                    difference_reserve = line.dependable_amount - line.practical_amount
                    sum_reserve += line.reserve_amount
                    row += 1
                    worksheet.write(row, col, "%s" %line.dependable_amount, bold_center_wrap)
                    col += 1
                    worksheet.write(row, col, "%s" %line.practical_amount, bold_center_wrap)
                    col += 1
                    worksheet.write(row, col, "%s" %line.reserve_amount, bold_center_wrap)
                else:
                    col+= 1
                    sum_reserve += line.reserve_amount
                    worksheet.write(row, col, "%s" %line.reserve_amount, bold_center_wrap)
                    
            
                    
                    