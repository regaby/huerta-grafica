# -*- coding: utf-8 -*-
##############################################################################
#
#    Soltic SRL
#    Copyright (C) 2011 Soltic SRL (<http://www.soltic.com.ar>).
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
from datetime import datetime, timedelta, time
from report import report_sxw
from report.report_sxw import rml_parse
from datetime import datetime
from dateutil import tz

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('Argentina/Buenos_Aires')

class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'get_objects':self._get_objects,
            'group':self._group,
            'group_items':self._group_items,
        })
        
    ret = False

    def _get_objects(self):

        if self.ret:
            return self.ret
        ret=[]
        cr = self.cr 
        uid = self.uid
        form = self.localcontext['data']['form']
        fecha_desde = form['fecha_desde'] 
        fecha_hasta = form['fecha_hasta'] 
        picking_pool = self.pool.get('stock.picking')
        employee_obj = self.pool.get('hr.employee')
        product_obj = self.pool.get('product.product')
        if form['agente_id']:
            employee_ids = [form['agente_id'][0]]
        elif form['unidad_organizativa_id']:
            employee_ids = employee_obj.search(cr, uid, [('department_id', '=', form['unidad_organizativa_id'][0])])
        else:
            employee_ids = employee_obj.search(cr, uid, [])

        if form['product_id']:
            product_ids = [form['product_id'][0]]
        else:
            product_ids = product_obj.search(cr, uid, [('product_order','=',True)])


        pick_ids = picking_pool.search(cr, uid, [('product_order','=',True),('date','>=',fecha_desde),('date','<=',fecha_hasta),
                                                 ('state','=','done'),('type','=','internal'),('employee_id','in',employee_ids),
                                                 ('product_id','=',product_ids)])
        for pick_obj in picking_pool.browse(cr, uid, pick_ids):
            for line in pick_obj.move_lines:
                res = {
                    'agente': pick_obj.employee_id.name,
                    'fecha': pick_obj.date,
                    'unidad_organizativa': pick_obj.employee_id.department_id.name, 
                    'product': line.product_id.name,
                    'qty': line.product_qty, 
                }
                ret.append(res)
        return ret
  


    def _group(self, attr, field):
        group = []
        for obj in attr:
            call = obj[field]
            if not {field: call} in group:
                group.append({field: call})
        return group

    def _group_items(self, attr, group, field):
        callg = group[field]
        items = []
        for obj in attr:
            call = obj[field]
            if call==callg:
                items.append(obj)
        return items
