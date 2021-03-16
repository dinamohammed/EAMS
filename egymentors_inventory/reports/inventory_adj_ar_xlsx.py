from odoo import models


class InventoryAdjustmentArXLSX(models.AbstractModel):
    _name = 'report.egymentors_inventory.report_inv_adj_ar_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        for obj in lines:
            if len(lines.ids) > 1:
                break
            report_name = obj.name
            worksheet = workbook.add_worksheet(report_name[:31])

            # Format
            worksheet.set_column('A:A', 18)
            worksheet.set_column('B:B', 12)
            worksheet.set_column('C:C', 10)
            worksheet.set_column('F:F', 12)
            worksheet.set_column('H:H', 10)
            worksheet.set_column('J:J', 12)
            sheet_header = workbook.add_format(
                {'font_size': 14, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#898a8c'})
            format_label = workbook.add_format(
                {'font_size': 10, 'align': 'center', 'bold': True, 'fg_color': '#898a8c'})
            format_value = workbook.add_format({'font_size': 10, 'align': 'center', 'fg_color': '#FFFFFF'})
            format_header_label_right = workbook.add_format(
                {'font_size': 10, 'align': 'right', 'bold': True, 'fg_color': '#898a8c'})
            format_header_label_left = workbook.add_format(
                {'font_size': 10, 'align': 'left', 'bold': True, 'fg_color': '#898a8c'})
            format_header_value_right = workbook.add_format({'font_size': 10, 'align': 'right', 'fg_color': '#898a8c'})

            # Sheet Header
            row = 0
            column = 0
            worksheet.write(row, column, 'اسم الجهة', format_header_label_right)
            worksheet.write(row, column + 1, obj.company_id.name, format_header_label_right)
            worksheet.write(row, column + 2, '', format_header_label_right)
            worksheet.write(row, column + 3, '', format_header_label_right)
            row += 1
            worksheet.write(row, column, 'المخزن', format_header_label_right)
            location_list = lines.location_ids.mapped('name')
            worksheet.merge_range(row, column + 1, row, column + 3, ', '.join(location_list), format_header_value_right)
            row += 1
            worksheet.write(row, column, 'تاريخ الجرد', format_header_label_right)
            worksheet.write(row, column + 1, obj.date.strftime('%d-%m-%Y'), format_header_value_right)
            worksheet.write(row, column + 2, 'مرجع الجرد', format_header_label_right)
            worksheet.write(row, column + 3, obj.name, format_header_value_right)
            row = 0
            worksheet.merge_range(row, column + 4, row + 2, column + 7, "محضر جرد الاصناف", sheet_header)
            worksheet.merge_range(row, column + 8, row + 2, column + 8, '', format_header_label_right)
            worksheet.merge_range(row, column + 9, row, column + 11, '(نموزج 9 مخازن حكومة)',
                                  format_header_label_left)
            row += 1
            worksheet.merge_range(row, column + 9, row, column + 11, '', format_header_label_right)
            row += 1
            worksheet.merge_range(row, column + 9, row, column + 11, "اسم صاحب العهدة",
                                  format_header_label_right)
            row += 1
            worksheet.merge_range(row, column, row, column + 11, '', format_value)

            # Table Header
            row += 1
            worksheet.write(row, column, 'رقم الصنف', format_label)
            column += 1
            worksheet.write(row, column, 'اسم الصنف', format_label)
            worksheet.merge_range(row, column, row, column + 2, 'اسم الصنف', format_label)
            column += 3
            worksheet.write(row, column, 'الوحدة', format_label)
            column += 1
            worksheet.write(row, column, 'الموجود من واقع الجرد', format_label)
            column += 1
            worksheet.write(row, column, 'حالة الصنف', format_label)
            column += 1
            worksheet.write(row, column, 'الرصيد الدفتري', format_label)
            column += 1
            worksheet.write(row, column, 'حالة الصنف', format_label)
            column += 1
            worksheet.write(row, column, 'التكلفة', format_label)
            column += 1
            worksheet.write(row, column, 'الفارق', format_label)
            column += 1
            worksheet.write(row, column, 'القيمة', format_label)

            # Lines:
            for stock_line in obj.line_ids:
                row += 1
                column = 0
                worksheet.write(row, column, stock_line.product_id.barcode, format_value)
                column += 1
                worksheet.merge_range(row, column, row, column + 2, stock_line.product_id.name, format_value)
                column += 3
                worksheet.write(row, column, stock_line.product_uom_id.name, format_value)
                column += 1
                worksheet.write(row, column, stock_line.product_qty, format_value)
                column += 1
                worksheet.write(row, column, '', format_value)
                column += 1
                worksheet.write(row, column, stock_line.theoretical_qty, format_value)
                column += 1
                worksheet.write(row, column, '', format_value)
                column += 1
                worksheet.write(row, column, stock_line.product_id.standard_price, format_value)
                column += 1
                worksheet.write(row, column, stock_line.difference_qty, format_value)
                column += 1
                worksheet.write(row, column, (stock_line.product_qty * stock_line.product_id.standard_price),
                                format_value)
            row += 1
            column = 0
            worksheet.write(row, column, 'توقيع كاتب الشطب', format_label)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, 'توقيع صاحب العهدة', format_label)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.merge_range(row, column, row, column + 1, 'توقيع لجنة الجرد', format_label)
            column += 2
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, 'مدير المخازن', format_label)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, 'رئيس المصلحة', format_label)

            row += 1
            column = 0
            worksheet.write(row, column, '', format_label)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_label)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.merge_range(row, column, row, column + 1, '', format_label)
            column += 2
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_label)
            column += 1
            worksheet.write(row, column, '', format_value)
            column += 1
            worksheet.write(row, column, '', format_label)

            row += 1
            column = 0
            worksheet.merge_range(row, column, row + 1, column + 4, '', format_value)
            column = 5
            worksheet.merge_range(row, column, row, column + 1, '', format_label)
            row += 1
            worksheet.merge_range(row, column, row, column + 1, '', format_label)
            column += 2
            worksheet.merge_range(row - 1, column, row, column + 4, '', format_value)
