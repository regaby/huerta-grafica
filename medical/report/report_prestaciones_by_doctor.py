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
            ## Atencion programada a domicilio
            'get_objects':self._get_objects,
            'group':self._group,
            'group_items':self._group_items,
            'get_total_doctor':self._get_total_doctor,
            'get_total':self._get_total,
        })
        
    def _get_objects(self):
        ret=[]
        cr = self.cr 
        uid = self.uid
        form = self.localcontext['data']['form']
        periodo = form['year'] 
        doctor_id = form['doctor_id']
        w_and = ''
        if doctor_id:
            w_and = 'and doctor = %d'%(doctor_id[0])
        sql = """select doc.name as doctor, pat.name as patient, count(*) as cantidad
                from medical_prestaciones_by_doctor_view v
                join res_partner doc on (doc.id=v.doctor)
                join res_partner pat on (pat.id=v.patient)
                where  year='%s'
                %s
                group by doc.name, pat.name
                order by doc.name
            """%(periodo,w_and)
        cr.execute(sql)
        ret = cr.dictfetchall()
        
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

    def _get_total_doctor(self, attr):
        # este metodo calcula total de prestaciones de un médico
        # se lo invoca como _get_lineas_prestaciones(group1.doctor)
        ret = []
        cr = self.cr 
        uid = self.uid
        form = self.localcontext['data']['form']
        periodo = form['year'] 
        sql = """select count(*) as total
                from medical_prestaciones_by_doctor_view v
                join res_partner doc on (doc.id=v.doctor)
                where  year='%s'
                and doc.name='%s'
                group by doc.name
            """%(periodo, attr)
        cr.execute(sql)
        ret = cr.dictfetchall()
        return ret[0]['total']

    def _get_total(self):
        # este metodo calcula total de prestaciones de un médico
        # se lo invoca como _get_lineas_prestaciones(group1.doctor)
        ret = []
        cr = self.cr 
        uid = self.uid
        form = self.localcontext['data']['form']
        periodo = form['year'] 
        doctor_id = form['doctor_id']
        w_and = ''
        if doctor_id:
            w_and = 'and doctor = %d'%(doctor_id[0])
        sql = """select count(*) as total
                from medical_prestaciones_by_doctor_view v
                where  year='%s'
                %s
            """%(periodo, w_and)
        cr.execute(sql)
        ret = cr.dictfetchall()
        return ret[0]['total']