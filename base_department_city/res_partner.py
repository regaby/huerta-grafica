# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import datetime
from lxml import etree
import math
import pytz
import re

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools.yaml_import import is_comment

from openerp.addons.base.res.res_partner import format_address

class res_partner(osv.osv, format_address):
    _description = 'Partner'
    _inherit = "res.partner"
        
    _columns = {
        
        'city_id' : fields.many2one('res.department.city','City', required=True),
        'department_id': fields.related('city_id','department_id', relation='res.state.department', string='Department', type='many2one', readonly=True),
        'state_rel_id': fields.related('department_id','state_id', relation='res.country.state', string='State', type='many2one', readonly=True),
        'country_rel_id': fields.related('state_rel_id','country_id', relation='res.country', string='Country', type='many2one', readonly=True),
    }


    def onchange_city(self, cr, uid, ids, city_id, context=None):
        if city_id:
            city = self.pool.get('res.department.city').browse(cr, uid, city_id, context)
            val = {'country_rel_id':city.department_id.state_id.country_id.id,
                   'state_rel_id':city.department_id.state_id.id,
                   'department_id':city.department_id.id,}
            # set zip city only if zip is empty
            partner = self.read(cr, uid, ids, ['zip'])
            if len(partner)==0 or not partner[0]['zip']:
                val['zip'] = city.zip_city
            return {'value': val}
        return {}
        
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context={}
        if vals.get('zip'):
            if not vals.get('zip').isdigit():
                 raise osv.except_osv(_('Warning!'), _('The zip must be un numeric') )
        return super(res_partner,self).write(cr, uid, ids, vals, context)
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
