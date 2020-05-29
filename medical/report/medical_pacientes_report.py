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
            'get_total':self._get_total,
        })

    def get_where_especialidad(self, codigo, signo):
        return "and (select count(*) from medical_prestaciones_by_doctor_view where speciality_id=%s and patient=x.patient and care_type=x.care_type) %s 0"%(codigo, signo)

    def init_variables(self, form):
        f_desde = form['date_from']
        f_hasta = form['date_to']
        care_type = form['care_type']
        insurance = form['insurance_id']
        psiq = form['psiquiatria']
        psicol = form['psicologia']
        psicop = form['psicopedadogia']
        print (form)
        w_care_type = w_insurance = w_psiq = w_psicol = w_psicop = ''
        if care_type:
            w_care_type = """where care_type = '%s'"""%(care_type)
        if insurance:
            w_insurance = "and mi.id = %s"%(insurance[0])
        if psiq:
            w_psiq = self.get_where_especialidad('5', '>')
        else:
            w_psiq = self.get_where_especialidad('5', '=')
        if psicol:
            w_psicol = self.get_where_especialidad('1000', '>')
        else:
            w_psicol = self.get_where_especialidad('1000', '=')
        if psicop:
            w_psicop = self.get_where_especialidad('32', '>')
        else:
            w_psicop = self.get_where_especialidad('32', '=')
        return f_desde, f_hasta, w_care_type, w_insurance, w_psiq, w_psicol, w_psicop

    def _get_objects(self):
        ret=[]
        cr = self.cr
        uid = self.uid
        form = self.localcontext['data']['form']
        f_desde, f_hasta, w_care_type, w_insurance, w_psiq, w_psicol, w_psicop = self.init_variables(form)
        sql = """with  medical_prestaciones_by_doctor_view as (
                    select id, patient, speciality_id, care_type, insurance_id, doctor
                    from medical_prestaciones_by_doctor_view
                    where f_fecha_practica between '%s 00:00:00' and '%s 23:59:59'
                )
                select min(x.id) as id, patient,p.name pat_name, care_type, mi.name financiadora,
                (case care_type when '1' then 'ATENCION PROGRAMADA A DOMICILIO' else
                    (case care_type when '2' then 'URGENCIAS A DOMICILIO' else
                    (case care_type when '3' then 'ATENCION TELEFONICA' else
                    (case care_type when '4' then 'CONSULTORIO EXTERNO' else
                    (case care_type when '5' then 'HOSPITAL DE DIA J. SIMPLE' else
                    (case care_type when '6' then 'HOSPITAL DE DIA J. COMPLETA' else
                    (case care_type when '7' then 'ATENCION JURISDICCIONES ALEJADAS' end) end) end) end) end) end) end) as modalidad,
                (select count(*) from medical_prestaciones_by_doctor_view v where v.speciality_id=5 and v.patient=x.patient and care_type=x.care_type) as psiq,
                (select count(*) from medical_prestaciones_by_doctor_view v where v.speciality_id=1000 and v.patient=x.patient and care_type=x.care_type) as psicol,
                (select count(*) from medical_prestaciones_by_doctor_view v where v.speciality_id=32 and v.patient=x.patient and care_type=x.care_type) as psicop,
                (select name from res_partner where id in (select v.doctor from medical_prestaciones_by_doctor_view v where v.speciality_id=5 and v.patient=x.patient and care_type=x.care_type)) as psiq_doc,
                (select name from res_partner where id in (select v.doctor from medical_prestaciones_by_doctor_view v where v.speciality_id=1000 and v.patient=x.patient and care_type=x.care_type)) as psicol_doc,
                (select name from res_partner where id in (select min(v.doctor) from medical_prestaciones_by_doctor_view v where v.speciality_id=32 and v.patient=x.patient and care_type=x.care_type)) as psicop_doc
                from medical_prestaciones_by_doctor_view as x
                join res_partner as p on (x.patient=p.id)
                join medical_insurance mi on (x.insurance_id=mi.id)
                %s
                %s
                %s
                %s
                %s
                group by patient, p.name,care_type, mi.name
                order by financiadora, p.name
            """%(f_desde, f_hasta, w_care_type, w_insurance, w_psiq, w_psicol, w_psicop)
        cr.execute(sql)
        print (cr.query)
        ret = cr.dictfetchall()
        return ret


    def _get_total(self):
        lista = self._get_objects()
        return len(lista)
