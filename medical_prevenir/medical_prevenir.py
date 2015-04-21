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
    _columns = {
        'is_patient' : fields.boolean('Patient', help="Check if the partner is a patient"),
        'is_doctor' : fields.boolean('Doctor', help="Check if the partner is a doctor"),
        'is_person' : fields.boolean('Person', help="Check if the partner is a person"),
        'is_institution' : fields.boolean ('Institution', help="Check if the partner is a Medical Center"),
        'lastname' : fields.char('Last Name', size=128, help="Last Name"),
    }
    
#
#    def name_get(self, cr, uid, ids, context=None):
#        if context is None:
#            context = {}
#        if not len(ids):
#            return []
#        if context.get('show_ref'):
#            rec_name = 'ref'
#        else:
#            rec_name = 'name'
#        list_ids = ids
#        if type(ids) == list and (type(ids[0]) == str or type(ids[0]) == unicode):
#            list_ids = []
#            for idx in ids:
#                list_ids.extend(self.search(cr, uid, [(rec_name, 'ilike', idx)]))
#        elif type(ids) == str or type(ids) == unicode:
#            list_ids = []
#            list_ids.extend(self.search(cr, uid, [(rec_name, 'ilike', ids)]))
#        res = [(r['id'], r[rec_name]) for r in self.read(cr, uid, list_ids, [rec_name], context)]
#        return res
medical_partner()

class medical_insurance(osv.osv):
    _name='medical.insurance'
    _columns={
        'name': fields.char('Name',size=128, required=True),

    }
medical_insurance()

# PATIENT GENERAL INFORMATION
class medical_patient (osv.osv):

    _patient_age_fnt = lambda self, cr, uid, ids, name, arg, context={}: self._patient_age(cr, uid, ids, name, arg, context)

    _name = "medical.patient"
    _description = "Patient related information"
    _inherits = {'res.partner': 'partner_id'}

    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Contact Details', required="1", domain=[('is_patient', '=', '1')], help="Patient Name", ondelete='cascade'),
        'partner_photo': fields.related('partner_id', 'image', type='binary', readonly=True),
        'partner_phone': fields.related('partner_id', 'phone', type='char', readonly=True),
        'partner_email': fields.related('partner_id', 'email', type='char', readonly=True),
        'partner_mobile': fields.related('partner_id', 'mobile', type='char', readonly=True),
        'partner_street': fields.related('partner_id', 'street', type='char', readonly=True),
        'partner_city': fields.related('partner_id', 'city', type='char', readonly=True),
        #----- datos paciente
        'age' : fields.function(_patient_age_fnt, method=True, type='char', size=32, string='Patient Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
        'dob' : fields.date ('Date of Birth'),
        'deceased' : fields.boolean ('Deceased', help="Mark if the patient has died"),
        'dod' : fields.datetime ('Date of Death'),
        'sex' : fields.selection([
            ('m', 'Male'),
            ('f', 'Female'),
        ], 'Sex', select=True),
        # ---- obra social
        'insurance_id': fields.many2one('medical.insurance','Insurance'),
        'insurance_number': fields.char('Insurance Number', size=64, required=True, select=True, ),
        'dni': fields.char('DNI', size=64, required=True, select=True, help="DNI"),
        'critical_info' : fields.text ('Important disease, allergy or procedures information', help="Write any important information on the patient's disease, surgeries, allergies, ..."),

        # extras
        #'primary_care_doctor': fields.many2one('medical.physician', 'Primary Care Doctor', help="Current primary care / family doctor"),
        
        # 'blood_type' : fields.selection([
        #     ('A', 'A'),
        #     ('B', 'B'),
        #     ('AB', 'AB'),
        #     ('O', 'O'),
        # ], 'Blood Type'),
        # 'rh' : fields.selection([
        #     ('+', '+'),
        #     ('-', '-'),
        # ], 'Rh'),
        # 'marital_status' : fields.selection([
        #     ('s', 'Single'),
        #     ('m', 'Married'),
        #     ('w', 'Widowed'),
        #     ('d', 'Divorced'),
        #     ('x', 'Separated'),
        #     ('f', 'Free Union'),
        # ], 'Marital Status'),
    }

    _defaults = {
        #'patient_id': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'medical.patient'),
        'is_patient': lambda obj, cr, uid, context: True
    }

    _sql_constraints = [
        ('dni_uniq', 'unique (dni)', 'The dni already exists')
    ]

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name', '')
            idx = d.get('patient_id', False)
            if idx:
                name = '[%s] %s' % (idx, name)
            return (d['id'], name)
        result = map(_name_get, self.read(cr, user, ids, ['name', 'patient_id'], context))
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

#    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
#        result = super(medical_patient, self).fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
#        if view_type == 'form':
#            partner_data = self.pool.get('res.partner').fields_view_get(cr, user, view_id=False, view_type='form', context=context, toolbar=toolbar, submenu=submenu)
#            result['fields'].update(partner_data['fields'])
#            arch = etree.fromstring(result['arch'])
#            arch_partner = etree.fromstring(partner_data['arch'])
#            patient = arch.xpath("//group[@name='medical.patient']")[0]
#            data_container = arch_partner.xpath("//sheet/group")[0]
#            data_container.addnext(patient)
##            patient.getparent().remove(patient)
#            details = arch.xpath("//notebook[@name='medical.patient.details']")[0]
#            history = arch_partner.xpath("//notebook/page[@name='page_history']")[0]
#            for child in details:
#                history.addprevious(child)
#
#            arch_partner = etree.tostring(arch_partner, encoding="utf-8").replace('\t', '')
#            result['arch'] = arch_partner
#        return result


medical_patient()