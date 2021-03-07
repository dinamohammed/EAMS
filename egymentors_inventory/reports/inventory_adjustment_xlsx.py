from odoo import models


class InventoryAdjustmentXLSX(models.AbstractModel):
    _name = 'report.egymentors_inventory.report_inventory_adjustment_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        worksheet = workbook.add_worksheet('Inventory Adjustment')

        # Format
        worksheet.set_column('A:A', 18)
        worksheet.set_column('B:B', 12)
        worksheet.set_column('C:C', 22)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 12)
        sheet_header = workbook.add_format(
            {'font_size': 14, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#898a8c'})
        format_label = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True, 'fg_color': '#898a8c'})
        format_value_bold = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'bold': True, 'fg_color': '#E4E2E2'})
        format_value_bold_left = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'bold': True, 'fg_color': '#E4E2E2'})
        format_value = workbook.add_format({'font_size': 10, 'align': 'center'})
        format_header_label = workbook.add_format(
            {'font_size': 10, 'align': 'right', 'bold': True, 'fg_color': '#898a8c'})
        format_header_value = workbook.add_format({'font_size': 10, 'align': 'left', 'fg_color': '#898a8c'})

        # Sheet Header
        row = 0
        column = 0
        worksheet.write(row, column, 'Organization Name: ', format_header_label)
        worksheet.write(row, column + 1, '', format_header_label)
        worksheet.write(row, column + 2, '', format_header_label)
        worksheet.write(row, column + 3, '', format_header_label)
        row += 1
        worksheet.write(row, column, 'Warehouse: ', format_header_label)
        location_list = lines.location_ids.mapped('name')
        worksheet.merge_range(row, column + 1, row, column + 3, ', '.join(location_list), format_header_value)
        row += 1
        worksheet.write(row, column, 'Inventory Date From: ', format_header_label)
        date_list = [d.strftime('%d-%m-%Y') for d in lines.mapped('date')]
        worksheet.write(row, column + 1, max(date_list), format_header_value)
        worksheet.write(row, column + 2, 'Date To: ', format_header_label)
        worksheet.write(row, column + 3, min(date_list), format_header_value)
        row = 0
        worksheet.merge_range(row, column + 4, row + 2, column + 6, "Inventory Adjustment", sheet_header)
        worksheet.merge_range(row, column + 7, row, column + 9, 'Form No. 9 Inventory .....', format_header_label)
        row += 1
        worksheet.merge_range(row, column + 7, row, column + 9, '', format_header_label)
        row += 1
        worksheet.merge_range(row, column + 7, row, column + 9, "Custody Keeper Name: ..............",
                              format_header_label)

        # Table Header
        row += 2
        worksheet.write(row, column, 'Date', format_label)
        column += 1
        worksheet.write(row, column, 'Code', format_label)
        column += 1
        worksheet.write(row, column, 'Product Name', format_label)
        column += 1
        worksheet.write(row, column, 'UoM', format_label)
        column += 1
        worksheet.write(row, column, 'Counted', format_label)
        column += 1
        worksheet.write(row, column, 'حالة الصنف', format_label)
        column += 1
        worksheet.write(row, column, 'On Hand', format_label)
        column += 1
        worksheet.write(row, column, 'حالة الصنف', format_label)
        column += 1
        worksheet.write(row, column, 'Difference', format_label)
        column += 1
        worksheet.write(row, column, 'State', format_label)

        # Adjustment Lines
        for line in lines:
            row += 1
            column = 0
            worksheet.write(row, column, str(line.date.date()), format_value_bold)
            column += 1
            worksheet.write(row, column, line.ref, format_value_bold)
            column += 1
            location_list = lines.location_ids.mapped('name')
            worksheet.write(row, column, ', '.join(location_list), format_value_bold_left)
            column += 1
            worksheet.write(row, column, '', format_value_bold)
            column += 1
            worksheet.write(row, column, '', format_value_bold)
            column += 1
            worksheet.write(row, column, line.display_name, format_value_bold)
            column += 1
            worksheet.write(row, column, '', format_value_bold)
            column += 1
            worksheet.write(row, column, '', format_value_bold)
            column += 1
            worksheet.write(row, column, '', format_value_bold)
            column += 1
            worksheet.write(row, column, line.state, format_value_bold)
            for stock_line in line.line_ids:
                row += 1
                column = 1
                worksheet.write(row, column, '', format_value)
                column += 1
                worksheet.write(row, column, stock_line.product_id.name, format_value)
                column += 1
                worksheet.write(row, column, stock_line.product_uom_id.name, format_value)
                column += 1
                worksheet.write(row, column, stock_line.product_qty, format_value)
                column += 1
                worksheet.write(row, column, 'حالة الصنف', format_value)
                column += 1
                worksheet.write(row, column, stock_line.theoretical_qty, format_value)
                column += 1
                worksheet.write(row, column, 'حالة الصنف', format_value)
                column += 1
                worksheet.write(row, column, stock_line.difference_qty, format_value)
