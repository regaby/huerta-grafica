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
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

from lxml import etree
import re

class calendar_event (osv.osv):
    _inherit = "calendar.event"

    def onchange_appointment_id (self, cr, uid, ids, appointment_id, context):
        values={}
        if appointment_id:
            appointment_obj = self.pool.get('medical.appointment').browse(cr,uid, appointment_id)
            if appointment_obj.care_type not in ('5','6'):
                values['consultorio_externo'] =  True
            else:
                values['consultorio_externo'] =  False
        return {'value': values}

    def write(self, cr, uid, ids, vals, context=None):
        print vals
        print vals
        print vals

        return super(calendar_event, self).write(cr, uid, ids, vals, context=context)

    _columns = {
        'patient' : fields.many2one ('res.partner','Patient', domain=[('is_patient', '=', "1")], help="Patient Name", required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'practice_id' : fields.many2one ('medical.practice', 'Practice', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'appointment_id' : fields.many2one ('medical.appointment', 'Appointment', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        # 'f_fecha_practica': fields.datetime('Practice Date', required=True, readonly=True, states={'Borrador':[('readonly',False)]}),
        'doctor_id' : fields.many2one ('res.partner', 'Especialista',domain=[('is_doctor', '=', "1")], help="Physician's Name", required=True, readonly=True, states={'draft':[('readonly',False)]}),
        # 'state': fields.selection([
        #     ('Borrador', 'Agendado'),
        #     ('Presente', 'Presente'),
        #     ('Ausente', 'Ausente'),
        # ], 'State', size=16, readonly=True),
        # 'comments' : fields.text ('Comments'),
        'insurance_id':fields.related('patient', 'insurance_id', type='many2one', relation='medical.insurance', string='Financiadora', readonly=True),
        'consultorio_externo': fields.boolean('Consultorio Externo'),
        'name': fields.char('Meeting Subject', required=False),
        'state': fields.selection([('draft', 'Unconfirmed'), ('open', 'Confirmed'),('done', 'Presente'),('declined', 'Ausente')], string='Status', readonly=True, track_visibility='onchange'),
        'description': fields.text('Description', readonly=False),
    }
    # _order = ""
    _defaults = {
        # 'state': 'Borrador',
        'name': '.'
    }
    _sql_constraints = [
        ('code_uniq', 'unique (patient,start_datetime)', 'La práctica debe ser única por horario')
    ]

    def action_present(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        turno = self.browse(cr, uid, ids, context=context)
        practice = {
        	'practice_id': turno.practice_id.id,
        	'appointment_id': turno.appointment_id.id,
        	'f_fecha_practica': turno.start_datetime,
        	'doctor_id': turno.doctor_id.id,
        	'q_cantidad': 1,
        }
        
        self.pool.get('medical.appointment.practice').create(cr, uid, practice)
        return True

    def action_absent(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'declined'})
        return True
    
calendar_event()