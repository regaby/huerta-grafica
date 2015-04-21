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

# DEBUG MODE -- DELETE ME !
# import pdb

class medical_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    _patient_age_fnt = lambda self, cr, uid, ids, name, arg, context={}: self._patient_age(cr, uid, ids, name, arg, context)

    _columns = {
        'is_patient' : fields.boolean('Patient', help="Check if the partner is a patient"),
        'is_doctor' : fields.boolean('Doctor', help="Check if the partner is a doctor"),
        'is_person' : fields.boolean('Person', help="Check if the partner is a person"),
        'is_institution' : fields.boolean ('Institution', help="Check if the partner is a Medical Center"),
        'lastname' : fields.char('Last Name', size=128, help="Last Name"),

        # --- datos paciente
        'age' : fields.function(_patient_age_fnt, method=True, type='char', size=32, string='Patient Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
        'dob' : fields.date ('Date of Birth'),
        'deceased' : fields.boolean ('Deceased', help="Mark if the patient has died"),
        'dod' : fields.datetime ('Date of Death'),
        'insurance': fields.char('Insurance', size=64, required=True, select=True, ),
        'insurance_number': fields.char('Insurance Number', size=64, required=True, select=True, ),
        'dni': fields.char('DNI', size=64, required=True, select=True, help="DNI"),
        'critical_info' : fields.text ('Important disease, allergy or procedures information', help="Write any important information on the patient's disease, surgeries, allergies, ..."),
        'sex' : fields.selection([
            ('m', 'Male'),
            ('f', 'Female'),
        ], 'Sex', select=True),
        'sex' : fields.selection([
            ('m', 'Male'),
            ('f', 'Female'),
        ], 'Sex', select=True),
        # ----- datos medico
        'registration_number': fields.char('Registration Number', size=64, required=True, select=True, ),
        'speciality' : fields.char('Speciality', size=64, required=True, select=True, ),
    }
    _sql_constraints = [
        ('dni_uniq', 'unique (dni)', 'The dni already exists')
    ]

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name', '')
            lastname = d.get('lastname', '')
            print name
            print lastname
            #idx = d.get('patient_id', False)
            # if idx:
            #     name = '[%s] %s' % (idx, name)
            complete_name = '%s, %s' % (lastname,name)
            return (d['id'], complete_name)
        result = map(_name_get, self.read(cr, user, ids, ['name', 'lastname'], context))
        print result
        return result

    # Get the patient age in the following format : "YEARS MONTHS DAYS"
    # It will calculate the age of the patient while the patient is alive. When the patient dies, it will show the age at time of death.
    def _patient_age(self, cr, uid, ids, name, arg, context={}):
        def compute_age_from_dates (patient_dob, patient_deceased, patient_dod):
            now = datetime.now()
            if (patient_dob):
                dob = datetime.strptime(patient_dob, '%Y-%m-%d')
                if patient_deceased :
                    dod = datetime.strptime(patient_dod, '%Y-%m-%d %H:%M:%S')
                    delta = relativedelta.relativedelta(dod, dob)
                    deceased = " (deceased)"
                else:
                    delta = relativedelta.relativedelta(now, dob)
                    deceased = ''
                years_months_days = str(delta.years) + "y " + str(delta.months) + "m " + str(delta.days) + "d" + deceased
            else:
                years_months_days = "No DoB !"

            return years_months_days
        result = {}
        for patient_data in self.browse(cr, uid, ids, context=context):
            result[patient_data.id] = compute_age_from_dates (patient_data.dob, patient_data.deceased, patient_data.dod)
        return result

medical_partner()

class medical_appointment (osv.osv):
    _name = "medical.appointment"
    
    _columns = {
        'doctor' : fields.many2one ('res.partner', 'Physician',domain=[('is_doctor', '=', "1")], help="Physician's Name"),
        'name' : fields.char ('Appointment ID', size=64, readonly=True, required=False),
        'patient' : fields.many2one ('res.partner','Patient', domain=[('is_patient', '=', "1")], help="Patient Name"),
        'appointment_date' : fields.datetime ('Date and Time'),
        'institution' : fields.many2one ('res.partner', 'Health Center', domain=[('is_institution', '=', "1")], help="Medical Center"),
        #'speciality' : fields.many2one ('medical.speciality', 'Speciality', help="Medical Speciality / Sector"),
        'speciality' : fields.char('Speciality', size=64, required=True, select=True, ),
        'state': fields.selection([
            ('draft', 'Unconfirmed'),
            ('open', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
            ('invoiced', 'Invoiced')
        ], 'State', size=16, readonly=True),
        # 'urgency' : fields.selection([
        #     ('a', 'Normal'),
        #     ('b', 'Urgent'),
        #     ('c', 'Medical Emergency'),
        # ], 'Urgency Level'),

        'comments' : fields.text ('Comments'),

# Additions from Husen Daudi (hda)
        'user_id':fields.related('doctor', 'user_id', type='many2one', relation='res.partner', string='Physician'),

# End of additions from hda

        'care_type': fields.selection([
            ('consul_ext', 'Consultorio Externo'),
            ('atenc_domic', 'Atención Programada a Domicilio'),
            ('atenc_juris', 'Atención en Jurisdicciónes Alejadas'),
            ('hosp_jorn_simple', 'Hospital de Dia Jornada Simple'),
            ('hosp_jorn_comple', 'Hospital de Dia Jornada Completa'),
            ('atenc_telef', 'Atencion Telefonica'),
            ('urgencia_dom', 'Urgencias en Domicilio'),

        ], 'Care Type'), ##---- Tipo de atencion
    }
    _order = "appointment_date desc"

    _defaults = {
        #'urgency': lambda *a: 'a',
        'name': lambda self, cr, uid, context = None: \
            self.pool.get('ir.sequence').get(cr, uid, 'medical.appointment'),
        'appointment_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'care_type': lambda *a: 'consul_ext',
        # TODO: arreglar esto
        #'doctor': lambda self, cr, uid, context: self.pool.get('medical.physician')._get_default_doctor(cr, uid, context),
        'state':lambda *a: 'draft',
    }

    # Additions from Nhomar Hernandez (nhomar)

    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'medical.appointment'),
        })
        return super(medical_appointment, self).copy(cr, uid, ids, default, context=context)

# End of additions from nhomar

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, uid, ids, ['rec_name', 'appointment_date'], context):
            date = str(r['appointment_date'] or '')
            res.append((r['id'], date))
        return res

    def onchange_doctor (self, cr, uid, ids, doctor, context):
        values={}
        if doctor:
            doctor_id = self.pool.get('res.partner').browse(cr,uid, doctor)
            values['speciality'] =  doctor_id.speciality

        return {'value': values}
    
    # def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
    #     if not context:
    #         context = {}
    #     if context.get('current_user', False):
    #         doctor_id = self.pool.get('medical.physician')._get_default_doctor(cr, uid, context)
    #         current_user = [('doctor', '=', doctor_id)]
    #         args.extend(current_user)
    #     return osv.osv.search(self, cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)

medical_appointment()
