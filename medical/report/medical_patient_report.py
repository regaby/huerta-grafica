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
from openerp.report import report_sxw
from openerp.report.report_sxw import rml_parse
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
            'get_total':self._get_total,
        })
        
    ret = False

    def _get_appoints(self):
        if self.ret:
            return self.ret
        ret=[]
        cr = self.cr 
        uid = self.uid
        form = self.localcontext['data']['form']
        fecha_desde = form['date_from'] 
        fecha_hasta = form['date_to'] 
        # picking_pool = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        # product_obj = self.pool.get('product.product')
        appointment_obj = self.pool.get('medical.appointment')
        if form['patient_id']:
            patient_ids = [form['patient_id'][0]]
        else:
            patient_ids = partner_obj.search(cr, uid, [('is_patient','=',True)])

        if form['doctor_id']:
            doctor_ids = [form['doctor_id'][0]]
        else:
            doctor_ids = partner_obj.search(cr, uid, [('is_doctor','=',True)])


        appoint_ids = appointment_obj.search(cr, uid, [('appointment_date','>=',fecha_desde),('appointment_date','<=',fecha_hasta),
                                                 ('patient','in',patient_ids),
                                                 ('doctor','in',doctor_ids)])
        return appoint_ids

    def _get_objects(self):
        if self.ret:
            return self.ret
        ret=[]
        cr = self.cr 
        uid = self.uid

        appoint_ids = self._get_appoints()

        appointment_obj = self.pool.get('medical.appointment')

        
        for appoint in appointment_obj.browse(cr, uid, appoint_ids):
            res = {
                'patient': appoint.patient.name,
                'fecha': appoint.appointment_date,
                'doctor': appoint.doctor.name, 
                'count': len(appoint_ids),
                # 'product': line.product_id.name,
                # 'qty': line.product_qty, 
            }
            ret.append(res)
        return ret

    def _get_total(self):
        appoint_ids = self._get_appoints()
        tot = len(appoint_ids)
        return tot
  


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
