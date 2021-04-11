# -*- coding: utf-8 -*-
#################################################################################
# Author      : TagElMaaly
# Copyright(c): 2021-Present EgyMentors.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.egymentors.com/>
#################################################################################

{
    "name": "Tender Request",
    "summary": "This module allow employees/users to create Tender Requests.",
    #"version": "14.0.1",
    "description": """ """,
    "author": "TagElMaaly",
    "maintainer": "",
    #"license" :  "Other proprietary",
    "website": "https://www.egymentors.com/",
    "images": ["images/tender_request.jpg"],
    "category": "Warehouse",
    "depends": [
        "stock",
        "hr",
        "purchase",
        "base",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/tender_request_data.xml",
        "data/mail_template_data.xml",
        "report/internal_requisition_report.xml",
        "report/internal_requisition_report_templates.xml",
        "views/tender_request_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_department_view.xml",
        "views/stock_picking_view.xml",
        "views/res_users_views.xml",
    ],
    "qweb": [],
    "installable": True,
    "application": True,
    "price"                :  45,
    "currency"             :  "EUR",
}
