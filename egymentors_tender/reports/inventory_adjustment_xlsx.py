from odoo import models, _


class InventoryAdjustmentXLSX(models.AbstractModel):
    _name = 'report.egymentors_tender.report_inventory_adjustment_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, adjustment):
        for line in adjustment:
            worksheet = workbook.add_worksheet(_('Inventory Adjustment'))

            # Format
            worksheet.set_column('A:A', 18)
            worksheet.set_column('B:B', 12)
            worksheet.set_column('C:C', 18)
            worksheet.set_column('E:E', 10)
            worksheet.set_column('F:F', 11)
            worksheet.set_column('H:H', 11)
            worksheet.set_column('J:J', 12)
            sheet_header = workbook.add_format(
                {'font_size': 14, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#898a8c'})
            format_label = workbook.add_format(
                {'font_size': 10, 'align': 'center', 'bold': True, 'fg_color': '#898a8c'})
            format_value = workbook.add_format({'font_size': 10, 'align': 'center', 'fg_color': '#FFFFFF'})
            format_header_label = workbook.add_format(
                {'font_size': 10, 'align': 'right', 'bold': True, 'fg_color': '#898a8c'})
            format_header_value = workbook.add_format({'font_size': 10, 'align': 'left', 'fg_color': '#898a8c'})

            # Sheet Header
            row = 0
            column = 0
            worksheet.write(row, column, _('Authority Name'), format_header_label)
            worksheet.write(row, column + 1, '', format_header_label)
            worksheet.write(row, column + 2, '', format_header_label)
            worksheet.write(row, column + 3, '', format_header_label)
            row += 1
            worksheet.write(row, column, _('Warehouse'), format_header_label)
            location_list = adjustment.location_ids.mapped('name')
            worksheet.merge_range(row, column + 1, row, column + 3, ', '.join(location_list), format_header_value)
            row += 1
            worksheet.write(row, column, _('Inventory Date'), format_header_label)
            worksheet.write(row, column + 1, line.date.strftime('%d-%m-%Y'), format_header_value)
            worksheet.write(row, column + 2, _('Inventory Reference'), format_header_label)
            worksheet.write(row, column + 3, line.name, format_header_value)
            row = 0
            worksheet.merge_range(row, column + 4, row + 2, column + 7, _("Inventory Adjustment"), sheet_header)
            worksheet.merge_range(row, column + 8, row + 2, column + 8, '', format_header_label)
            worksheet.merge_range(row, column + 9, row, column + 11, _('(Form No. 9 Inventory government)'),
                                  format_header_label)
            row += 1
            worksheet.merge_range(row, column + 9, row, column + 11, '', format_header_label)
            row += 1
            worksheet.merge_range(row, column + 9, row, column + 11, _("Custody Keeper Name: .............."),
                                  format_header_label)
            row += 1
            worksheet.merge_range(row, column, row, column + 11, '', format_value)

            # Table Header
            row += 1
            column = 0
            worksheet.write(row, column, _('Code'), format_label)
            column += 1
            worksheet.merge_range(row, column, row, column + 2, _('Product Name'), format_label)
            column += 3
            worksheet.write(row, column, _('UoM'), format_label)
            column += 1
            worksheet.write(row, column, _('Counted'), format_label)
            column += 1
            worksheet.write(row, column, _('Product State'), format_label)
            column += 1
            worksheet.write(row, column, _('On Hand'), format_label)
            column += 1
            worksheet.write(row, column, _('Product State'), format_label)
            column += 1
            worksheet.write(row, column, _('Cost'), format_label)
            column += 1
            worksheet.write(row, column, _('Difference'), format_label)
            column += 1
            worksheet.write(row, column, _('Value'), format_label)

            for stock_line in line.line_ids:
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
