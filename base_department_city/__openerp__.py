# -*- coding: utf-8 -*-
##############################################################################
#
#    Module for Openerp
#    Copyright (C) 2013 Soltic SRL (<http://soltic.com.ar>)
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Base Department City",
    "version": "1.0",
    "author": "Soltic SRL",
    "category": "Hidden",
    "website": "http://www.soltic.com.ar",
    "description": """
Extension base module to add department and city under state
===================================================
- Add res.state.department entity
- Add res.department.city entity
- Update res.partner and res.partner.form view with these entities
- Update res.company and res.company.form view with these entities
- Add Cuit field to res.partner
    """,
    'depends': [
                'base',
               ],
    'init_xml': [],
    'update_xml': [
                   'res_country_view.xml',
                   'res_partner_view.xml',
                   'res_company_view.xml',
                  ],
    'data': [
            'security/ir.model.access.csv',
            ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

