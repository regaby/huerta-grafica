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
            'get_total_pacientes': self._get_total_pacientes,
            '_get_lineas_prestaciones':self._get_lineas_prestaciones,
            '_get_lineas_cant_pacientes': self._get_lineas_cant_pacientes,
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
        practice_obj = self.pool.get('calendar.event')
        # patient_ids = []
        # if form['patient_id']:
        #     patient_ids = [form['patient_id'][0]]
        # if form['doctor_id']:
        #     doctor_ids = [form['doctor_id'][0]]
        # elif form['city_id']:
        #     doctor_ids = partner_obj.search(cr, uid, [('city_id','=',form['city_id'][0]),('is_doctor','=',True)])
        # else:
        #     doctor_ids = partner_obj.search(cr, uid, [('is_doctor','=',True)])

        practice_ids = practice_obj.search(cr, uid, [('start_datetime','>=',fecha_desde),('start_datetime','<=',fecha_hasta),
                                                 ('state','=','declined')
                                                 ],order="start_datetime")
        ret=[]

        # for practice in practice_obj.browse(cr, uid, practice_ids):
        #     tot=0
        #     if len(patient_ids)>0:
        #         if practice.appointment_id.patient.id != patient_ids[0]:
        #             continue
        #     ret.append(practice.id)

        return practice_ids 

    def _get_objects(self):
        if self.ret:
            return self.ret
        ret=[]
        cr = self.cr 
        uid = self.uid

        practice_ids = self._get_practices()
        practice_obj = self.pool.get('calendar.event')
        partner_obj = self.pool.get('res.partner')
        form = self.localcontext['data']['form']
        patient_ids=[]
        # if form['patient_id']:
        #     patient_ids = [form['patient_id'][0]]
        for practice in practice_obj.browse(cr, uid, practice_ids):
            tot=0
            # if len(patient_ids)>0:
            #     if practice.appointment_id.patient.id != patient_ids[0]:
            #         continue
            #for practice in appoint.practice_ids:
            tot += 1
            res = {
                'patient': practice.patient.name,
                'fecha': practice.start_datetime[8:10]+'/'+practice.start_datetime[5:7]+'/'+practice.start_datetime[0:4]+' '+practice.start_datetime[11:16],
                #'fecha': practice.appointment_id.appointment_date,
                #'doctor': practice.appointment_id.doctor.name, 
                'doctor': practice.doctor_id.name, 
                'q_cantidad': 1,
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
        practice_obj = self.pool.get('calendar.event')
        for practice in practice_obj.browse(cr, uid, practice_ids):
            tot += 1
        return tot

    def _get_total_pacientes(self):
        # este método calcula total del reporte
        # se invoca como: get_total_pacientes()
        cr = self.cr 
        uid = self.uid
        practice_ids = self._get_practices()
        tot = 0
        patient=[]
        practice_obj = self.pool.get('calendar.event')
        for practice in practice_obj.browse(cr, uid, practice_ids):
            patient.append(practice.appointment_id.patient.id)
        patient = list(set(patient))
        return len(patient)

    def _get_lineas_prestaciones(self, attr):
        # este metodo calcula total de prestaciones de un médico
        # se lo invoca como _get_lineas_prestaciones(group1.doctor)
        ret = []
        cr = self.cr 
        uid = self.uid
        subtotal = 0
        form = self.localcontext['data']['form']
        practice_ids = self._get_practices()
        practice_obj = self.pool.get('calendar.event')
        for practice in practice_obj.browse(cr, uid, practice_ids):
            if practice.patient.name==attr:
                subtotal+=1
        return subtotal

    def _get_lineas_cant_pacientes(self, attr):
        # este metodo calcula total de prestaciones de un médico
        # se lo invoca como _get_lineas_cant_pacientes(group1.doctor)<_get_lineas_cant_pacientes(group1.doctor)>
        ret = []
        cr = self.cr 
        uid = self.uid
        subtotal = 0
        form = self.localcontext['data']['form']
        patient=[]
        practice_ids = self._get_practices()
        practice_obj = self.pool.get('calendar.event')
        for practice in practice_obj.browse(cr, uid, practice_ids):
            if practice.patient.name==attr:
                patient.append(practice.appointment_id.patient.id)
        patient = list(set(patient))
        return len(patient)
  
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
