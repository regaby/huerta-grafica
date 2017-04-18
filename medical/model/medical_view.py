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
from openerp.osv import fields, osv
from openerp import tools
import time
from datetime import datetime
import calendar
from openerp.tools.translate import _

class medical_prestaciones_view(osv.osv):
    _name = 'medical.prestaciones.view'
    _auto = False
    _order = 'create_date desc'

    def _get_year(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for practice in self.browse(cr, uid, ids, context=context):
            cr.execute('''select f_fecha_practica from medical_appointment_practice where id = %d'''%(practice.id))
            fech = cr.fetchall()
            if fech:
                res[practice.id] = fech[0][0][0:7]
        return res

    def _search_year(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        res = []
        if args[0][1]in ('ilike'):
            year = args[0][2][0:4]
            month = args[0][2][5:7]
            
            try:
                to_date = datetime(int(year), int(month), 1)
            except:
                raise osv.except_osv(_('Error'),_('El periodo debe tener el formado AAAA-MM') )  

            last_day = calendar.monthrange(int(year),int(month))[1]
            cr.execute("""select id from medical_appointment_practice where f_fecha_practica between '%s-01 00:00:00' and '%s-%s 23:59:59'"""%(args[0][2],args[0][2],last_day))
            print cr.query
            res = cr.fetchall()
            
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(lambda x:x[0], res))]

    _columns = {
    	'doctor': fields.many2one('res.partner', 'Especialista', readonly=True),
    	'doc_specility': fields.char('Especialidad', readonly=True),
    	'doc_city_id': fields.many2one('res.department.city', 'Cuidad Profesional', readonly=True),
    	'pat_benefit_code': fields.char('Beneficiario', readonly=True),
    	'pat_relationship_code': fields.char('Parentesco', readonly=True),
    	'patient': fields.many2one('res.partner', 'Afiliado', readonly=True),
    	'appointment_date': fields.date('Fecha Atención', readonly=True),
    	'care_type': fields.selection([
            ('1','Atención Programada a Domicilio'),
            ('2','Urgencias en Domicilio'),
            ('3','Atención telefónica'),
            ('4', 'Consultorio Externo'),
            ('5', 'Hospital de Dia Jornada Simple'),
            ('6', 'Hospital de Dia Jornada Completa'),
            ('7', 'Atención en Jurisdicciónes Alejadas'),
        ], 'Tipo de Atención'), ##---- Tipo de atencion
        'pat_diagnostic_name': fields.char('Diagnóstico', readonly=True),
        'f_fecha_practica': fields.datetime('Fecha de práctica', readonly=True),
        'pat_practice_name': fields.char('Práctica', readonly=True),
        'appointment_id': fields.many2one('medical.appointment', 'Prestación', readonly=True),
        'id_modalidad_presta': fields.char('id_modalidad_presta', readonly=True),
        'f_fecha_egreso': fields.date('Fecha Egreso', readonly=True),
        'id_tipo_egreso': fields.char('id_tipo_egreso', readonly=True),
        'comments': fields.char('comments', readonly=True),
        'pat_diagnostic_code': fields.char('pat_diagnostic_code', readonly=True),
        'm_tipo_diagnostico': fields.char('m_tipo_diagnostico', readonly=True),
        'pat_practice_code': fields.char('pat_practice_code', readonly=True),
        'q_cantidad': fields.integer('Cantidad', readonly=True),
        'afiliado': fields.char('Afiliado', readonly=True),
        'create_uid': fields.many2one('res.users', 'Creado por', readonly=True),
        'create_date': fields.date('Fecha creación', readonly=True),
        'year': fields.function(_get_year,fnct_search=_search_year, method=True, type= 'char', string='Periodo'),  
    }

    def init(self, cr):
      tools.drop_view_if_exists(cr, 'medical_prestaciones_view')
      cr.execute("""
            CREATE OR REPLACE VIEW medical_prestaciones_view AS
                select map.id, doc.name as doc_name , ms.name as doc_specility, ms.code doc_code, doc.registration_number as doc_registration_number, doc.state_registration_number as doc_state_registration_number, 
					doc.document_type as doc_document_type, doc.dni as doc_dni, doc.cuil as doc_cuil, doc.street as doc_street, doc.street_number as doc_street_number, 
					city.zip_city as doc_zip_city, doc.city_id as doc_city_id, doc.phone as doc_phone, doc.start_date as doc_start_date, mb.code as pat_benefit_code, mbt.code as pat_benefit_type_code, 
					mb.name as pat_benefit_name, mb.start_date, pat.name as pat_name, pat.document_type as pat_document_type, pat.dni as pat_dni, pat.marital_status as pat_marital_status, 
					pat.nacionality as pat_nacionality, rc.code as pat_nationality_code, pat.street as pat_street, pat.street_number as pat_street_number,pat_city.zip_city as pat_zip_city, 
					pat.city_id as pat_city_id, pat.attention_city_id , pat.attention_department_id , pat.phone as pat_phone, pat.dob as pat_dob, pat.sex as pat_sex, pat.cuil as pat_cuil, pat.cuit as pat_cuit, mpr.code as pat_relationship_code,
					ma.appointment_date, ma.id_modalidad_presta, ma.care_type, ma.f_fecha_egreso, ma.id_tipo_egreso, ma.comments, md.code as pat_diagnostic_code, mad.m_tipo_diagnostico,
					f_fecha_practica, q_cantidad, mp.code as pat_practice_code, pat.end_date as pat_end_date, md.name as pat_diagnostic_name, mp.name as pat_practice_name,
					ma.doctor, ma.patient, map.appointment_id, mb.code || mpr.code as afiliado,
                    map.create_uid, map.create_date::date
				from medical_appointment_practice map
					join medical_appointment ma on (map.appointment_id=ma.id)
					join res_partner doc on (ma.doctor=doc.id)
					join medical_speciality ms on (doc.speciality_id=ms.id)
					left join res_department_city city on (doc.city_id=city.id)
					join res_partner pat on (ma.patient=pat.id)
					join medical_benefit mb on (pat.benefit_id=mb.id)
					left join medical_benefit_type mbt on (mb.benefit_type_id=mbt.id)
					left join res_country rc on (pat.nacionality_id=rc.id)
					left join res_department_city pat_city on (pat.city_id=pat_city.id)
					join medical_patient_relationship mpr on (pat.relationship_id=mpr.id)
					join medical_appointment_diagnostic mad on (mad.appointment_id=ma.id)
					left join medical_diagnostic md on (mad.diagnostic_id=md.id)
					join medical_practice mp on (map.practice_id=mp.id)
                    join medical_insurance mi on (mb.insurance_id=mi.id)
				where pat.end_date is null
                and mi.code ='PAMI'
            """)

medical_prestaciones_view()  