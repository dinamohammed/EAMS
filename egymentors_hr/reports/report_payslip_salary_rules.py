# -*- coding: utf-8 -*-
import base64
import io
import math
from odoo import models, fields


# Ahmed Salama Code Start ---->


class PayslipXlsx(models.AbstractModel):
    _name = 'report.egymentors_hr.report_payslip_salary_rules'
    _inherit = 'report.report_xlsx.abstract'
    
    def generate_xlsx_report(self, workbook, data, payslips):
        report_name = "عناصر اجر الموظفين"
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
        worksheet.set_column('C:X', 8)
        bold = workbook.add_format({'bold': True})
        # Company Logo
        company_logo = self.env.user.company_id.logo
        imgdata = base64.b64decode(company_logo)
        image = io.BytesIO(imgdata)
        batch_name = payslips[0].payslip_run_id and payslips[0].payslip_run_id.name or ''
        worksheet.insert_image('G1', 'myimage.png', {'image_data': image, 'x_scale': 1, 'y_scale': 0.5})
        # worksheet.merge_range(1, 6, 1, 8, self.env.user.company_id.name or '')
        # worksheet.merge_range(2, 4, 2, 8, self.env.user.street or '')
        worksheet.write(2, 2, "%s عناصر اجر الموظفين بتاريخ" % fields.Date.today(), bold)
        worksheet.merge_range(3, 1, 3, 3, batch_name, bold)
        cell_format_header_parent = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                                         'border': 1, 'fg_color': '#898a8c'})
        cell_format_header = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter',
                                                  'border': 1, 'fg_color': '#898a8c'})
        cell_format_row = workbook.add_format({'bold': False, 'align': 'center', 'valign': 'vcenter',
                                               'border': 1})
        cell_format_signature = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
        cell_format_header_parent.set_center_across()
        cell_format_header.set_center_across()
        salary_rules_obj = self.env['hr.salary.rule']
        salary_rule_parent_obj = self.env['hr.salary.rule.parent']
        row = 6
        # Get Active Salary Rules
        salary_rule_parent, rules_without_parent = payslips.assign_parents_and_free_rules()
        
        # Main Headers
        worksheet.merge_range(row-1, 0, row, 0, 'م', cell_format_header_parent)
        worksheet.merge_range(row-1, 1, row, 1, 'إسم الموظف', cell_format_header_parent)
        
        # Print Rule/Parent Name
        col = 2
        if salary_rule_parent:
            for parent in salary_rule_parent:
                parent_id = salary_rule_parent_obj.browse(parent)
                worksheet.merge_range(row-1, col, row, col+1, parent_id.name, cell_format_header_parent)
                worksheet.write(row, col+1, "جنيه", cell_format_header_parent)
                worksheet.write(row, col, "قرشاً", cell_format_header_parent)
                col += 2
        if rules_without_parent:
            for rule in rules_without_parent:
                rule_id = salary_rules_obj.browse(rule)
                worksheet.merge_range(row-1, col, row, col+1, rule_id.name, cell_format_header)
                worksheet.write(row, col+1, "جنيه", cell_format_header_parent)
                worksheet.write(row, col, "قرشاً", cell_format_header_parent)
                col += 2
        worksheet.merge_range(row-1, col, row, col, 'حساب بنك الموظف', cell_format_header_parent)
        row += 1
        
        # Print Values
        for idx, payslip_id in enumerate(payslips):
            worksheet.write(row, 0, idx + 1, cell_format_row)
            worksheet.write(row, 1, payslip_id.employee_id.name, cell_format_row)
            col = 2
            if salary_rule_parent:
                for total in payslip_id.get_parent_amount(salary_rule_parent):
                    total_list = math.modf(total)
                    worksheet.write(row, col, total_list[0] and math.floor(abs(total_list[0]*100)) or 00, cell_format_row)
                    worksheet.write(row, col+1, total_list[1], cell_format_row)
                    # worksheet.write(row, col, total, cell_format_row)
                    col += 2
            
            if rules_without_parent:
                for total in payslip_id.get_free_rule_amount(rules_without_parent):
                    total_list = math.modf(total)
                    worksheet.write(row, col, total_list[0] and math.floor(abs(total_list[0]*100)) or 00, cell_format_row)
                    worksheet.write(row, col+1, total_list[1], cell_format_row)
                    # worksheet.write(row, col, total, cell_format_row)
                    col += 2
            
            bank = payslip_id.employee_id.bank_account_id and \
                   payslip_id.employee_id.bank_account_id.acc_number or '------------'
            worksheet.write(row, col, bank, cell_format_header_parent)
            row += 1
        # Print Totals
        worksheet.merge_range(row, 0, row, 1, 'الإجمالى', cell_format_header_parent)
        col = 2
        if salary_rule_parent:
            for total in payslips.get_parent_amount(salary_rule_parent):
                total_list = math.modf(total)
                worksheet.write(row, col, total_list[0] and math.floor(abs(total_list[0]*100)) or 00, cell_format_header_parent)
                worksheet.write(row, col+1, total_list[1], cell_format_header_parent)
                # worksheet.write(row, col, total, cell_format_header_parent)
                col += 2
        if rules_without_parent:
            for total in payslips.get_free_rule_amount(rules_without_parent):
                total_list = math.modf(total)
                worksheet.write(row, col, total_list[0] and math.floor(abs(total_list[0]*100)) or 00, cell_format_header_parent)
                worksheet.write(row, col+1, total_list[1], cell_format_header_parent)
                # worksheet.write(row, col, total, cell_format_header)
                col += 2
        row += 4
        worksheet.write(row, 1, "الإسـتـحـقـاقـات", cell_format_signature)
        worksheet.write(row, 3, "مـديـر المـوارد البـشريه", cell_format_signature)
        worksheet.write(row, 5, "مـراجعـه مـاليـه", cell_format_signature)
        worksheet.write(row, 7, "مـديـر المـراجعـه", cell_format_signature)

# Ahmed Salama Code End.
