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

class medical_prestaciones_by_speciality_view(osv.osv):
    _name = 'medical.prestaciones.by.speciality.view'
    _auto = False
    _order = 'year desc'

    _columns = {
    	'patient': fields.many2one('res.partner', 'Afiliado', readonly=True),
    	'psiq': fields.integer('Psiquiatria', readonly=True),
        'psicol': fields.integer('Psicologia', readonly=True),
        'psicop': fields.integer('Psicopedagogia', readonly=True),
        'year': fields.char('Período', readonly=True)
    }

    def init(self, cr):
      tools.drop_view_if_exists(cr, 'medical_prestaciones_by_speciality_view')
      cr.execute("""
            CREATE OR REPLACE VIEW medical_prestaciones_by_speciality_view AS
                with  medical_prestaciones_by_doctor_view as (
                    select id, patient, speciality_id,year
                    from medical_prestaciones_by_doctor_view 
                    --where year='2017-11'
                    --and patient=22596
                )
                select min(id) as id , year, patient,-- count(*)
                (select count(*) from medical_prestaciones_by_doctor_view where speciality_id=5 and patient=x.patient  ) as psiq,
                (select count(*) from medical_prestaciones_by_doctor_view where speciality_id=1000 and patient=x.patient ) as psicol,
                (select count(*) from medical_prestaciones_by_doctor_view where speciality_id=32 and patient=x.patient ) as psicop
                from medical_prestaciones_by_doctor_view as x
                group by patient, year
            """)

medical_prestaciones_by_speciality_view()  

