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
            'get_total_prestaciones':self._get_total_prestaciones,
            '_get_lineas_prestaciones':self._get_lineas_prestaciones,
        })
        
    ret = False

    def _get_practices(self):
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
        #appointment_obj = self.pool.get('medical.appointment')
        practice_obj = self.pool.get('medical.appointment.practice')
        patient_ids = []
        if form['patient_id']:
            patient_ids = [form['patient_id'][0]]
        if form['doctor_id']:
            doctor_ids = [form['doctor_id'][0]]
        elif form['city_id']:
            doctor_ids = partner_obj.search(cr, uid, [('city_id','=',form['city_id'][0]),('is_doctor','=',True)])
        else:
            doctor_ids = partner_obj.search(cr, uid, [('is_doctor','=',True)])

        # appoint_ids = appointment_obj.search(cr, uid, [('appointment_date','>=',fecha_desde),('appointment_date','<=',fecha_hasta),
        #                                          ('patient','in',patient_ids),
        #                                          ('doctor','in',doctor_ids)])
        # return appoint_ids
        practice_ids = practice_obj.search(cr, uid, [('f_fecha_practica','>=',fecha_desde),('f_fecha_practica','<=',fecha_hasta),
                                                 ('doctor_id','in',doctor_ids)
                                                 ],order="f_fecha_practica")
        ret=[]

        for practice in practice_obj.browse(cr, uid, practice_ids):
            tot=0
            if len(patient_ids)>0:
                if practice.appointment_id.patient.id != patient_ids[0]:
                    continue
            ret.append(practice.id)

        return ret 

    def _get_objects(self):
        if self.ret:
            return self.ret
        ret=[]
        cr = self.cr 
        uid = self.uid

        practice_ids = self._get_practices()
        practice_obj = self.pool.get('medical.appointment.practice')
        partner_obj = self.pool.get('res.partner')
        form = self.localcontext['data']['form']
        patient_ids=[]
        if form['patient_id']:
            patient_ids = [form['patient_id'][0]]
        for practice in practice_obj.browse(cr, uid, practice_ids):
            tot=0
            if len(patient_ids)>0:
                if practice.appointment_id.patient.id != patient_ids[0]:
                    continue
            #for practice in appoint.practice_ids:
            tot += practice.q_cantidad
            res = {
                'patient': practice.appointment_id.patient.name,
                'fecha': practice.f_fecha_practica[8:10]+'/'+practice.f_fecha_practica[5:7]+'/'+practice.f_fecha_practica[0:4]+' '+practice.f_fecha_practica[11:16],
                #'fecha': practice.appointment_id.appointment_date,
                #'doctor': practice.appointment_id.doctor.name, 
                'doctor': practice.doctor_id.name, 
                'q_cantidad': practice.q_cantidad,
            }
            ret.append(res)
        return ret

    def _get_total_prestaciones(self):
        # este método calcula total del reporte
        # se invoca como: _get_total_prestaciones()
        cr = self.cr 
        uid = self.uid
        practice_ids = self._get_practices()
        tot = 0
        practice_obj = self.pool.get('medical.appointment.practice')
        for practice in practice_obj.browse(cr, uid, practice_ids):
            tot += practice.q_cantidad
        return tot

    def _get_lineas_prestaciones(self, attr):
        # este metodo calcula total de prestaciones de un médico
        # se lo invoca como _get_lineas_prestaciones(group1.doctor)
        ret = []
        cr = self.cr 
        uid = self.uid
        subtotal = 0
        form = self.localcontext['data']['form']
        practice_ids = self._get_practices()
        practice_obj = self.pool.get('medical.appointment.practice')
        for practice in practice_obj.browse(cr, uid, practice_ids):
            if practice.doctor_id.name==attr:
                subtotal+=1
        return subtotal
  
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
