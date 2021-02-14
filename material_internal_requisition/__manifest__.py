# -*- coding: utf-8 -*-
#################################################################################
# Author      : CodersFort (<https://codersfort.com/>)
# Copyright(c): 2017-Present CodersFort.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://codersfort.com/>
#################################################################################

{
    "name": "Product/Material Internal Requisitions by Employees/Users",
    "summary": "This module allow employees/users to create Internal Requisitions.",
    "version": "13.0.1",
    "description": """
        This module allowed Internal requisition of employee.
        Material Internal Requisitions
        Material request is an instruction to procure a certain quantity of materials by Internal
        internal transfer or manufacturing.So that goods are available when it require
        Material request for Internal, internal transfer or manufacturing
        Material request for internal transfer
        Material request for Internal order
        Material request for Internal tender
        Material request for tender
        Material request for manufacturing order
        product request, subassembly request, raw material request, order request
        manufacturing request, Internal request, Internal tender request, internal transfer request
        Material Requisition for Internal, internal transfer or manufacturing
        Material Requisition for internal transfer
        Material Requisition for Internal order
        Material Requisition for Internal tender
        Material Requisition for tender
        Material Requisition for manufacturing order
        product Requisition for Internal, internal transfer or manufacturing
        product Requisition for internal transfer
        product Requisition for Internal order
        product Requisition for Internal tender
        product Requisition for tender
        product Requisition for manufacturing order
        product Internal requisition by employee
        product Internal requisition by users
        product Internal requisition for employee
        product Internal requisition for users
        material Internal requisition for employee
        material Internal requisition for users
        material Internal requisition by employee
        material Internal requisition by users
        Internal_Requisition_Via_iProcurement
        Internal Requisitions
        Internal Requisition
        iProcurement
        Inter-Organization Shipping Network
        Online Requisitions
        Issue Enforcement
        Inventory Replenishment Requisitions
        Replenishment Requisitions
        MRP Generated Requisitions
        generated Requisitions
        Internal Sales Orders
        Complete Requisitions Status Visibility
        Using Internal Requisitions
        Internal requisitions
        replenishment requisitions
        employee Requisition
        employee Internal Requisition
        user Requisition
        stock Requisition
        inventory Requisition
        warehouse Requisition
        factory Requisition
        department Requisition
        manager Requisition
        Submit requisition
        Create Internal Orders
        Internal Orders
        product Requisition
        item Requisition
        material Requisition
        product Requisitions
        material Internal Requisition
        material Requisition Internal
        Internal material Requisition
        product Internal Requisition
        item Requisitions
        material Requisitions
        products Requisitions
        Internal Requisition Process
        Approving or Denying the Internal Requisition
        Denying Internal Requisition​
        construction managment
        real estate management
        construction app
        Requisition
        Requisitions
        indent management
        indent
        indent stock
        indent system
        indent request
        indent order
        odoo indent
        internal Requisitions
        Internal.requisition search (search)
        Internal.requisition.form.view (form)
        Internal.requisition.view.tree (tree)
        Internal_requisition (qweb) """,
    "author": "CodersFort",
    "maintainer": "Ananthu Krishna",
    "license" :  "Other proprietary",
    "website": "http://www.codersfort.com",
    "images": ["images/material_internal_requisition.png"],
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
        "data/internal_requisition_data.xml",
        "data/mail_template_data.xml",
        "report/internal_requisition_report.xml",
        "report/internal_requisition_report_templates.xml",
        "views/internal_requisition_view.xml",
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
    "pre_init_hook"        :  "pre_init_check",   
    "live_test_url": "https://youtu.be/zld4fLHanEg",
}
