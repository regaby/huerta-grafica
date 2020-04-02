# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
{
    "name": "Medical",
    "author": "Gabriela Rivero",
    "category": "Medical",
    "description": """
This module provide :
        Medical functionality:
            - Patients
            - Physician
            - Appointments
    """,
    "version": "1.0",
    "depends": [
        "base",
        "base_department_city",
        'report_aeroo',
        ],

    "init_xml": [],
    'data': [
        ## VISTAS
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'wizard/efectores_pami_view.xml',
        'wizard/medical_patient_report_wizard_view.xml',
        'wizard/medical_patient_report_new.xml',
        'views/medical_view.xml',
        'views/medical_prestaciones_view.xml',
        'views/medical_prestaciones_by_pat_view.xml',
        'views/medical_prestaciones_by_doctor_view.xml',
        'views/medical_prestaciones_by_speciality_view.xml',
        'wizard/padron_pami_view.xml',
        # 'views/medical_turno_view.xml',
        'views/medical_insurance_view.xml',
        'views/medical_practice_view.xml',
        'views/medical_diagnostic_view.xml',
        ## MENU
        'views/medical_menu.xml',
        ## REPORTE
        'report/medical_patient_report.xml',
        ## DATA
        'data/medical_insurance.xml',
    ],
    'demo_xml': [],
    'images': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
