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

class medical_prestaciones_by_doctor_view(osv.osv):
    _name = 'medical.prestaciones.by.doctor.view'
    _auto = False
    # _order = 'create_date desc'

    _columns = {
    	'patient': fields.many2one('res.partner', 'Afiliado', readonly=True),
    	'doctor': fields.many2one('res.partner', 'Profesional', readonly=True),
    	'speciality_id': fields.many2one('medical.speciality', 'Especialidad', readonly=True),
    	'care_type': fields.selection([
            ('1','Atención Programada a Domicilio'),
            ('2','Urgencias en Domicilio'),
            ('3','Atención telefónica'),
            ('4', 'Consultorio Externo'),
            ('5', 'Hospital de Dia Jornada Simple'),
            ('6', 'Hospital de Dia Jornada Completa'),
            ('7', 'Atención en Jurisdicciónes Alejadas'),
        ], 'Tipo de Atención'), ##---- Tipo de atencion
        'year': fields.char('Período'),
        'insurance_id': fields.many2one('medical.insurance','Financiadora'),
    }

    def init(self, cr):
      tools.drop_view_if_exists(cr, 'medical_prestaciones_by_doctor_view')
      cr.execute("""
            CREATE OR REPLACE VIEW medical_prestaciones_by_doctor_view AS
                select map.id, ma.patient, map.doctor_id as doctor, doc.speciality_id, left(f_fecha_practica::text,7) as year, ma.care_type, doc.city_id as doc_city_id, mb.insurance_id
				from medical_appointment_practice map
				join medical_appointment ma on (map.appointment_id=ma.id)
				join res_partner doc on (map.doctor_id=doc.id)
				join medical_speciality ms on (doc.speciality_id=ms.id)
				left join res_department_city city on (doc.city_id=city.id)
				join res_partner pat on (ma.patient=pat.id)
				join medical_benefit mb on (pat.benefit_id=mb.id)
				join medical_insurance mi on (mb.insurance_id=mi.id)
			where pat.end_date is null
            --and mi.code ='PAMI'
            """)

medical_prestaciones_by_doctor_view()  

