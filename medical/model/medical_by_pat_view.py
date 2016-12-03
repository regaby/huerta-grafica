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

class medical_prestaciones_by_pat_view(osv.osv):
    _name = 'medical.prestaciones.by.pat.view'
    _auto = False
    # _order = 'create_date desc'

    

    _columns = {
    	'doc_city_id': fields.many2one('res.department.city', 'Cuidad Profesional', readonly=True),
    	'patient': fields.many2one('res.partner', 'Afiliado', readonly=True),
    	'care_type': fields.selection([
            ('1','Atención Programada a Domicilio'),
            ('2','Urgencias en Domicilio'),
            ('3','Atención telefónica'),
            ('4', 'Consultorio Externo'),
            ('5', 'Hospital de Dia Jornada Simple'),
            ('6', 'Hospital de Dia Jornada Completa'),
            ('7', 'Atención en Jurisdicciónes Alejadas'),
        ], 'Tipo de Atención'), ##---- Tipo de atencion
        'year': fields.char('Período')
        
    }

    def init(self, cr):
      tools.drop_view_if_exists(cr, 'medical_prestaciones_by_pat_view')
      cr.execute("""
            CREATE OR REPLACE VIEW medical_prestaciones_by_pat_view AS
                select min(id) as id, care_type, patient, doc_city_id, left(f_fecha_practica::text,7) as year
                from medical_prestaciones_view 
                group by care_type, patient, doc_city_id, left(f_fecha_practica::text,7)
            """)

medical_prestaciones_by_pat_view()  

