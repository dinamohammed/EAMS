from odoo import models, _
from datetime import datetime


class DetailedTaskSheetXLSX(models.AbstractModel):
    _name = 'report.egymentors_maintnance.detailed_task_sheet_excel_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        request_obj = self.env['maintenance.request']
        for task_sheet in lines:
            report_name = task_sheet.name
            worksheet = workbook.add_worksheet(report_name[:31])

            # Format
            worksheet.set_column('A:A', 10)  # Location
            worksheet.set_column('B:B', 10)  # Equipment
            worksheet.set_column('C:C', 18)  # Last Technical State
            worksheet.set_column('D:D', 24)  # Task
            worksheet.set_column('G:G', 18)  # Note
            worksheet.set_column('H:H', 24)  # Technical State After Maintenance
            worksheet.set_column('I:I', 18)  # Frequent faults
            worksheet.set_column('J:J', 24)  # Recurring Error During Contract

            sheet_header = workbook.add_format(
                {'font_size': 18, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'font_color': '#FFFFFF',
                 'fg_color': '#2B3856'})
            project_header = workbook.add_format(
                {'font_size': 14, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_color': '#FFFFFF',
                 'fg_color': '#2B547E'})
            column_header = workbook.add_format(
                {'font_size': 8, 'bold': True, 'align': 'center', 'valign': 'vcenter', 'font_color': '#FFFFFF',
                 'fg_color': '#737CA1'})
            loc_header = workbook.add_format(
                {'font_size': 8, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'fg_color': '#B4CFEC'})
            equip_header = workbook.add_format(
                {'font_size': 8, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'fg_color': '#D1D0CE'})
            value_right = workbook.add_format(
                {'font_size': 8, 'bold': True, 'align': 'right', 'valign': 'vcenter', 'fg_color': '#FFFFFF'})

            row = 0
            column = 0
            worksheet.merge_range(row, column, row + 2, column + 9, task_sheet.name, sheet_header)
            row = 3

            # PROJECT
            for project in task_sheet.project_ids:
                column = 0
                worksheet.merge_range(row, column, row + 1, column + 9, project.name, project_header)

                # Table Header 1
                row += 2
                worksheet.write(row, column, _('Location'), column_header)
                column += 1
                worksheet.write(row, column, _('Equipment'), column_header)
                column += 1
                worksheet.write(row, column, _('Last Technical State'), column_header)
                column += 1
                worksheet.merge_range(row, column, row, column + 3, _('Maintenance Tasks'), column_header)
                column += 4
                worksheet.write(row, column, _('Technical State After Maintenance'), column_header)
                column += 1
                worksheet.write(row, column, _('Frequent faults'), column_header)
                column += 1
                worksheet.write(row, column, _('Recurring Error During Contract'), column_header)

                # Table Header 2
                row += 1
                column = 0
                worksheet.merge_range(row, column, row, column + 2, '', column_header)
                column += 3
                worksheet.write(row, column, _('Task'), column_header)
                column += 1
                worksheet.write(row, column, _('Status'), column_header)
                column += 1
                worksheet.write(row, column, _('Readings'), column_header)
                column += 1
                worksheet.write(row, column, _('Note'), column_header)
                column += 1
                worksheet.merge_range(row, column, row, column + 2, '', column_header)
                row += 1

                # LOCATION
                locations = (project.location_ids.filtered(
                    lambda loc: loc.id in task_sheet.location_ids.ids
                )) if task_sheet.location_ids else project.location_ids
                for location in locations:
                    column = 0
                    worksheet.merge_range(row, column, row, column + 9, location.name, loc_header)
                    row += 1

                    # EQUIPMENT
                    equipments = (
                        location.equipment_ids.filtered(lambda equip: equip.id in task_sheet.equipment_ids.ids)
                    ) if task_sheet.equipment_ids else location.equipment_ids
                    for equipment in equipments:
                        column = 1
                        worksheet.merge_range(row, column, row, column + 8, equipment.name, equip_header)
                        column += 1

                        # TECHNICAL STATUS
                        status = task_sheet.technical_status_ids.filtered(
                            lambda sts: sts.equipment_id.id == equipment.id).ensure_one()
                        row += 1
                        worksheet.write(
                            row, column, status.last_technical_state, value_right
                        ) if status.last_technical_state else ""
                        column += 5
                        worksheet.write(row, column, status.state_after_maintenance, value_right)
                        column += 1
                        worksheet.write(row, column, status.repeated_errors, value_right)
                        column += 1

                        # Calculating Equipment Fault reoccurrence:
                        requests_count = request_obj.search_count([
                            ('equipment_id', '=', equipment.id),
                            ('maintenance_type', '=', 'corrective'),
                            ('equipment_id.installation_date', '<=', datetime.today()),
                            ('equipment_id.warranty_date', '>=', datetime.today()),
                        ])
                        worksheet.write(row, column, requests_count, value_right)

                        # TASKS
                        tasks = task_sheet.task_sheet_line_ids.filtered(lambda tsk: tsk.equipment_id.id == equipment.id)
                        row += 1
                        for task in tasks:
                            column = 3
                            worksheet.write(row, column, task.task_id.name, value_right)
                            column += 1
                            worksheet.write(row, column, task.state, value_right) if task.state else ""
                            column += 1
                            worksheet.write(row, column, task.readings, value_right) if task.readings else ""
                            column += 1
                            worksheet.write(row, column, task.note, value_right) if task.note else ""
                            column += 1
                            row += 1
                        row += 1
                    row += 1
