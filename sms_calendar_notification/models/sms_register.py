# coding=utf-8

#    Copyright (C) 2008-2010  Luis Falcon

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time
from datetime import date
from datetime import datetime, timedelta
from dateutil import relativedelta
import calendar

from openerp.osv import fields, osv
from openerp.tools.translate import _

from lxml import etree
import re
import requests

class sms_register (osv.osv):
    _name = "sms.register"
    _order = "id desc"

    _columns = {
        'date': fields.date('Fecha'),
        'state': fields.selection([
            ('draft', 'Borrador'),
            ('sended', 'Enviado')
        ], string='Status'),
        'log': fields.text(string='Log'),
        'count_ok': fields.integer(),
        'count_error': fields.integer(),
    }
    _defaults = {
        'state': 'draft',
    }

    def procesar_scheduler(self, cr, uid, context=None):
        NextDay_Date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        sms_register_obj = self.pool.get('sms.register')
        sms_register_id = sms_register_obj.create(cr, uid, {'date': NextDay_Date})
        sms_register_obj.procesar(cr, uid, sms_register_id, context)

    def procesar(self, cr, uid, ids, context=None):
        # buscar calendar.event del dia, filtrar por sms_notification
        # hacer un for y enviar sms
        output = ''
        calendar_obj = self.pool.get('calendar.event')
        company_obj = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        this = self.browse(cr, uid, ids)[0]
        usuario = company_obj.usuario_sms
        clave = company_obj.clave_sms
        count_ok = count_error = 0
        if not usuario or not clave:
            output += 'No se ha establecido el usuario y/o contraseña del servicio de sms.\n'
        event_ids = calendar_obj.search(cr, uid, [
            ('type', '=', 'event'),
            ('sms_notification', '=', True),
            ('start', '>', '%s 00:00:00'%this.date),
            ('start', '<', '%s 23:59:59'%this.date)])
        for event in calendar_obj.browse(cr, uid, event_ids):
            hora = (datetime(*time.strptime(event.start, "%Y-%m-%d %H:%M:%S")[0:5])-timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")
            sex_pat = event.patient.sex == 'F' and 'Sra.' or 'Sr.'
            sex_doc = event.doctor_id.sex == 'F' and 'la Dra.' or 'el Dr.'
            text = "%s %s recuerde su turno el %s hs. con %s. Red Prevenir"%(sex_pat, event.patient.name, hora, event.doctor_id.name)
            phone = event.phone and event.phone or event.patient.mobile
            if not phone:
                output += 'No hay telefono celular definido para el paciente %s\n'%event.patient.name
            sms = """http://servicio.smsmasivos.com.ar/enviar_sms.asp?api=1&usuario=%s&clave=%s&tos=%s&texto=%s"""%(usuario, clave, phone, text)
            res = requests.post(sms).text
            if res[0:2] != 'OK':
                output += "%s\n"%res
                count_error += 1
            else:
                count_ok += 1
            output += "Cantidad de mensaje enviados correctamente: %s\nCantidad de errres: %s\n"%(count_ok, count_error)
        self.write(cr, uid, ids, {'state': 'sended', 'log': output, 'count_ok': count_ok, 'count_error': count_error})



sms_register()
