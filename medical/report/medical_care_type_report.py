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
            'get_subtotal1':self._get_subtotal1,
            ## Urgencia a domicilio
            'get_objects2':self._get_objects2,
            'get_subtotal2':self._get_subtotal2,
            ## Atención telefonica
            'get_objects3':self._get_objects3,
            'get_subtotal3':self._get_subtotal3,
            ## Consultorio Externo
            'get_objects4':self._get_objects4,
            'get_subtotal4':self._get_subtotal4,
            ## Hospital de dia jornada simple
            'get_objects5':self._get_objects5,
            'get_subtotal5':self._get_subtotal5,
            ## Hospital de dia jornada completa
            'get_objects6':self._get_objects6,
            'get_subtotal6':self._get_subtotal6,
            ## Atencion en jurisdiccion alejada
            'get_objects7':self._get_objects7,
            'get_subtotal7':self._get_subtotal7,
            'get_total':self._get_total,
        })
        
        # ret = False

    def _get_sql(self,care_type):

        # if self.ret:
        #     return self.ret
        ret=[]
        cr = self.cr 
        uid = self.uid
        form = self.localcontext['data']['form']
        fecha_desde = form['date_from'] 
        fecha_hasta = form['date_to'] + ' 23:59:59'
        sql = """select 
            care_type, rp.name as name
            from medical_appointment_practice map
            join medical_appointment ma on (map.appointment_id=ma.id)
            join res_partner rp on (ma.patient=rp.id)
            where f_fecha_practica >= '%s'
            and f_fecha_practica < '%s'
            and care_type = '%s'
            group by care_type, rp.name
            """%(fecha_desde,fecha_hasta,care_type)
        cr.execute(sql)
        ret = cr.dictfetchall()
        
        return ret

    ## Atencion programada a domicilio
    def _get_objects(self, objects):
        ret = self._get_sql(1)
        return ret

    def _get_subtotal1(self):
        return len(self._get_sql(1))

    ## Urgencia a domicilio
    def _get_objects2(self, objects):
        ret = self._get_sql(2)
        return ret

    def _get_subtotal2(self):
        return len(self._get_sql(2))

    ## Atención telefonica
    def _get_objects3(self, objects):
        ret = self._get_sql(3)
        return ret

    def _get_subtotal3(self):
        return len(self._get_sql(3))

    ## Consultorio Externo
    def _get_objects4(self, objects):
        ret = self._get_sql(4)
        return ret

    def _get_subtotal4(self):
        return len(self._get_sql(4))

    ## Hospital de dia jornada simple
    def _get_objects5(self, objects):
        ret = self._get_sql(5)
        return ret

    def _get_subtotal5(self):
        return len(self._get_sql(5))

    ## Hospital de dia jornada completa
    def _get_objects6(self, objects):
        ret = self._get_sql(6)
        return ret

    def _get_subtotal6(self):
        return len(self._get_sql(6))

    ## Atencion en jurisdiccion alejada
    def _get_objects7(self, objects):
        ret = self._get_sql(7)
        return ret

    def _get_subtotal7(self):
        return len(self._get_sql(7))

    def _get_total(self):
        return len(self._get_sql(1))+len(self._get_sql(2))+len(self._get_sql(3))+len(self._get_sql(4))+len(self._get_sql(5))+len(self._get_sql(6))+len(self._get_sql(7))




