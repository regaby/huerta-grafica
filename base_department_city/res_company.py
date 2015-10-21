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
  
class res_company(osv.osv):
    
    _description = 'Companies'
    _inherit = "res.company"

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        return super(res_company, self)._get_address_data(cr, uid, ids, field_names, arg, context)
    
    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        return super(res_company, self)._set_address_data(cr, uid, company_id, name, value, arg, context)

    def onchange_city(self, cr, uid, ids, city_id, context=None):
        if city_id:
            city = self.pool.get('res.department.city').browse(cr, uid, city_id, context)
            val = {'country_rel_id':city.department_id.state_id.country_id.id,
                   'state_rel_id':city.department_id.state_id.id,
                   'department_id':city.department_id.id,}
            # set zip city only if zip is empty
            company = self.read(cr, uid, ids, ['zip'])
            if len(company)==0 or not company[0]['zip']:
                val['zip'] = city.zip_city
            return {'value': val}
        return {}

    _columns = {        
        'city_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', relation='res.department.city', string="City", multi='address'),
        'department_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', domain="[('state_rel_id', '=', state_rel_id)]", relation='res.state.department', string="Department", multi='address'),
        'state_rel_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', domain="[('country_rel_id', '=', country_rel_id)]", relation='res.country.state', string="Fed. State", multi='address'),
        'country_rel_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', relation='res.country', string="Country", multi='address'),
    }

res_company()
