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
import calendar

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

    def _check_days(self,cr,uid,ids,context=None):
        for holiday in self.browse(cr, uid, ids):
            if holiday.start and holiday.stop and holiday.type=='event':
                if holiday.start[0:10] == holiday.stop[0:10]:
                    holiday_ids = self.search(cr, uid, [('start','<',holiday.start),('stop','>',holiday.start),('patient','=',holiday.patient.id)])
                    if len(holiday_ids) > 0:
                        return False
        return True

    def _check_days_holiday(self,cr,uid,ids,context=None):
        for holiday in self.browse(cr, uid, ids):
            if holiday.start and holiday.stop and holiday.type=='holiday':
                if holiday.start[0:10] == holiday.stop[0:10]:
                    holiday_ids = self.search(cr, uid, [('start','<',holiday.start),('stop','>',holiday.start),('patient','=',holiday.patient.id)])
                    if len(holiday_ids) > 0:
                        return False
        return True

    def _check_holidays(self,cr,uid,ids,context=None):
        for holiday in self.browse(cr, uid, ids):
            if holiday.start and holiday.stop and holiday.type=='event':
                if holiday.start[0:10] == holiday.stop[0:10]:
                    holiday_ids = self.search(cr, uid, [('start','<',holiday.start),('stop','>',holiday.start),('doctor_id','=',holiday.doctor_id.id),('type','=','holiday')])
                    if len(holiday_ids) > 0:
                        return False
        return True

    def get_pami_link(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)
        url = 'http://institucional.pami.org.ar/result.php?c=6-2-1-1&beneficio=%s&parent=%s&vm=2'%(this.patient.benefit_id.code,this.patient.relationship_id.code)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
                }

    def unlink(self, cr, uid, ids, context=None):
        orden = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in orden:
            if s['state'] in ['draft','holiday']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('No se puede eliminar un turno que esté en estado presente o ausente'))
        return super(calendar_event, self).unlink(cr, uid, unlink_ids, context=context)

    def write(self, cr, uid,ids, vals, context=None):
        if 'start' in vals.keys():
            state = self.read(cr, uid, ids, ['state'], context=context)[0]['state']
            if state not in ['draft','holiday']:
                raise osv.except_osv(_('Invalid action !'), _('No se puede modificar la fecha de un turno que esté en estado presente o ausente'))
        if 'state' in vals.keys():
            # si el estado que quiero cambiar es = presente, controlo que la fecha del turno sea <= al dia de hoy
            if vals['state']=='done':
                start_datetime = self.read(cr, uid, ids, ['start_datetime'], context=context)[0]['start_datetime'][0:10]
                start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d')
                if start_datetime > datetime.now():
                    raise osv.except_osv(_('Invalid action !'), _('No se puede marcar como presente un turno posterior a la fecha actual'))
            recurrency = self.read(cr, uid, ids, ['recurrency'], context=context)[0]['recurrency']
            if recurrency:
                new_id = self._detach_one_event(cr, uid, ids[0], context=context)
                super(calendar_event, self).write(cr, uid, new_id, vals, context)
                return new_id
        super(calendar_event, self).write(cr, uid, ids, vals, context)
        return ids

    def _get_period(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for event in self.browse(cr, uid, ids, context=context):
            cr.execute('''select start from calendar_event where id = %d'''%(event.id))
            fech = cr.fetchall()
            if fech:
                res[event.id] = fech[0][0][0:7]
        return res

    def _search_period(self, cr, uid, obj, name, args, context=None):
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
            cr.execute("""select id from calendar_event where start between '%s-01 00:00:00' and '%s-%s 23:59:59'"""%(args[0][2],args[0][2],last_day))
            print cr.query
            res = cr.fetchall()
            
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(lambda x:x[0], res))]

    _columns = {
        'patient' : fields.many2one ('res.partner','Patient', domain=[('is_patient', '=', "1")], help="Patient Name", readonly=True, states={'draft':[('readonly',False)]}),
        'practice_id' : fields.many2one ('medical.practice', 'Practice', readonly=True, states={'draft':[('readonly',False)]}),
        'appointment_id' : fields.many2one ('medical.appointment', 'Appointment', readonly=True, states={'draft':[('readonly',False)]}),
        'doctor_id' : fields.many2one ('res.partner', 'Especialista',domain=[('is_doctor', '=', "1")], help="Physician's Name", readonly=True, required=True, states={'draft':[('readonly',False)],'holiday':[('readonly',False)]}),
        'insurance_id':fields.related('patient', 'insurance_id', type='many2one', relation='medical.insurance', string='Financiadora', readonly=True),
        'consultorio_externo': fields.boolean('Consultorio Externo'),
        'name': fields.char('Meeting Subject'),
        'state': fields.selection([('draft', 'Unconfirmed'), ('open', 'Confirmed'),('done', 'Presente'),('declined', 'Ausente'),('holiday', 'Licencia')], string='Status', track_visibility='onchange'),
        'description': fields.text('Description', readonly=False),
        'type': fields.selection([('event', 'Medical Event'), ('holiday', 'Holiday')], string='Type'),
        'create_user_id': fields.many2one ('res.users', 'Creado por', readonly=True),
        'period': fields.function(_get_period,fnct_search=_search_period, method=True, type= 'char', string='Periodo'),  
        'phone': fields.char('Telefono',size=20, readonly=True, states={'draft':[('readonly',False)]}),
    }
    _defaults = {
        'state': 'draft',
        'name': '.',
        'type': 'event',
        'create_user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id ,
        'duration': 1,
    }
    _sql_constraints = [
        ('code_uniq', 'unique (patient,start_datetime,recurrency)', 'Ya existe otro turno en el mismo horario para el paciente actual.')
    ]
    _constraints = [
        (_check_days, 'Ya existe otro turno en el mismo rango horario para el paciente actual!',['start']),
        (_check_days_holiday, 'Ya existe otra licencia en el mismo rango de dias para el profesional actual!',['start']),
        (_check_holidays, 'No se puede crear este turno porque el especialista tiene una licencia cargada este dia!',['doctor_id']),
    ] 

    def action_present(self, cr, uid, ids, context=None):
        new_id = self.write(cr, uid, ids, {'state': 'done'})
        if not isinstance(new_id, (int, long)):
            new_id = new_id[0]
        turno = self.browse(cr, uid, ids, context=context)
        practice = {
        	'practice_id': turno.practice_id.id,
        	'appointment_id': turno.appointment_id.id,
        	'f_fecha_practica': turno.start_datetime,
        	'doctor_id': turno.doctor_id.id,
        	'q_cantidad': 1,
            'calendar_event_id': new_id,
        }
        
        self.pool.get('medical.appointment.practice').create(cr, uid, practice)
        return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'calendar.event',
                    'view_mode': 'form',
                    'res_id': new_id,
                    'target': 'current',
                    # 'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
                }

    def action_absent(self, cr, uid, ids, context=None):
        new_id = self.write(cr, uid, ids, {'state': 'declined'})
        if not isinstance(new_id, (int, long)):
            new_id = new_id[0]
        return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'calendar.event',
                    'view_mode': 'form',
                    'res_id': new_id,
                    'target': 'current',
                    # 'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
                }

    def set_draft(self, cr, uid, ids, context=None):
        turno = self.browse(cr, uid, ids, context=context)
        practice_pool = self.pool.get('medical.appointment.practice')
        if turno.state=='declined':
            self.write(cr, uid, ids, {'state': 'draft'})
            return True
        else:
            turno_id = practice_pool.search(cr, uid, [('calendar_event_id','=',turno.id)])
            if turno_id:
                practice_pool.unlink(cr, uid, turno_id)
            else:
                turno_id = practice_pool.search(cr, uid, [('practice_id','=',turno.practice_id.id),
                                                          ('appointment_id','=',turno.appointment_id.id),
                                                          ('f_fecha_practica','=',turno.start_datetime),
                                                          ('doctor_id','=',turno.doctor_id.id),])
                if turno_id:
                    practice_pool.unlink(cr, uid, turno_id)
            self.write(cr, uid, ids, {'state': 'draft'})
            return True



    
calendar_event()