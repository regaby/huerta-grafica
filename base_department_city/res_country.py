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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import logging

class StateDepartment(osv.osv):
    
    _name = 'res.state.department'
    _description = 'Department of State'
    _columns = {
        
        'name': fields.char('Department', size=50, required=True),
        'zone': fields.integer('Zone', required=True),
        'state_id' : fields.many2one('res.country.state','State', required=False),
        
    }
    
    sql_constraints = [
        
        ('department_name_uniq', 'unique(state_id, name)', 'The Name must be Unique per State.'),
        
    ]
    
StateDepartment()

class DepartmentCity(osv.osv):
    
    _name = 'res.department.city'
    _description = 'City of Department'
    _columns = {
        
        'name': fields.char('City', size=50, required=True),
        'municipality': fields.integer('Municipality'),        
        'department_id' : fields.many2one('res.state.department','Department'), # 'state__id' : State relacion a "res.country.state
        'zip_city' : fields.integer('Zip'),
        
    }
    
    sql_constraints = [
        
        ('city_zipe_uniq', 'unique(zipe)', 'The zip must be unique.'),
        ('department_name_uniq', 'unique(department_id, name)', 'The Name must be Unique per Department.'),
        
    ]
    
DepartmentCity()

