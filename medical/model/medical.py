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
import logging

_logger = logging.getLogger(__name__)

CARE_TYPE = [
            ('1','Atención Programada a Domicilio'),
            ('2','Urgencias en Domicilio'),
            ('3','Atención telefónica'),
            ('4', 'Consultorio Externo'),
            ('5', 'Hospital de Dia Jornada Simple'),
            ('6', 'Hospital de Dia Jornada Completa'),
            ('7', 'Atención en Jurisdicciónes Alejadas'),
        ]


# DEBUG MODE -- DELETE ME !
# import pdb

class medical_speciality (osv.osv):
    _name = "medical.speciality"
    _columns = {
        'name' :fields.char ('Description', size=128, help="ie, Addiction Psychiatry", required="True"),
        'code' : fields.char ('Code', size=128, help="ie, ADP", required="True"),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (name)', 'The code must be unique')
    ]
medical_speciality ()

class medical_patient_relationship (osv.osv):
    _name = "medical.patient.relationship"
    _columns = {
        'name' :fields.char ('Description', size=128, required="True"),
        'code' : fields.char ('Code', size=2, required="True"),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'Code must be unique'),

    ]

    # def name_get(self, cr, user, ids, context={}):
    #     if not len(ids):
    #         return []
    #     def _name_get(d):
    #         name = d.get('name', '')
    #         code = d.get('code', '')
    #         #idx = d.get('patient_id', False)
    #         # if idx:
    #         #     name = '[%s] %s' % (idx, name)
    #         if code and name:
    #             complete_name = '%s - %s' % (code,name)
    #         else:
    #             complete_name = name
    #         return (d['id'], complete_name)
    #     result = map(_name_get, self.read(cr, user, ids, ['name', 'code'], context))
    #     return result


medical_patient_relationship ()

class medical_module (osv.osv):
    _name = "medical.module"
    _columns = {
        'name' :fields.char ('Description', size=128, required="True"),
        'code' : fields.char ('Code', size=2, required="True"),
        'level' : fields.char ('Level', size=2),
        'start_date': fields.date('Start Date', help="Fecha de alta de la relación entre modulo y prestador."),
        #'instution_id': fields.many2one('res.partner','Institution', required="True"),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique')
    ]
medical_module ()

class medical_subsidiary (osv.osv):
    _name = "medical.subsidiary"
    _columns = {
        'name' :fields.char ('Description', size=128, required="True"),
        'code' : fields.char ('Code', size=2, required="True"),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique')
    ]
medical_subsidiary ()

class medical_agency (osv.osv):
    _name = "medical.agency"
    _columns = {
        'name' :fields.char ('Description', size=128, required="True"),
        'code' : fields.char ('Code', size=2, required="True"),
        'subsidiary_id': fields.many2one('medical.subsidiary','Subsidiary',required=True),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code, subsidiary_id)', 'The code and subsidiary must be unique')
    ]
medical_agency ()

class medical_correspondent (osv.osv):
    _name = "medical.correspondent"
    _columns = {
        'name' :fields.char ('Description', size=128, required="True"),
        'code' : fields.char ('Code', size=2, required="True"),
        'subsidiary_id': fields.many2one('medical.subsidiary','Subsidiary',required=True),
        'agency_id': fields.many2one('medical.agency','Agency',required=False),
        'id_agencia': fields.integer('Id Agencia'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code, subsidiary_id, id_agencia)', 'The code and subsidiary and agency must be unique.')
    ]
medical_correspondent ()

class medical_afjp (osv.osv):
    _name = "medical.afjp"
    _columns = {
        'name' :fields.char ('Description', size=128, required="True"),
        'code' : fields.char ('Code', size=2, required="True"),
        'abbreviation' : fields.char ('Abbreviation', size=5, required="True"),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique')
    ]
medical_afjp ()

class Country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
        'code': fields.char('Country Code', size=3,
            help='The ISO country code in two chars.\n'
            'You can use this field for quick search.'),
        
    }
Country()

class DepartmentCity(osv.osv):
    
    _name = 'res.department.city'
    _inherit = 'res.department.city'
    _columns = {
        
        # 'name': fields.char('City', size=50, required=True),
        # 'municipality': fields.integer('Municipality'),        
        # 'department_id' : fields.many2one('res.state.department','Department'), # 'state__id' : State relacion a "res.country.state
        # 'zip_city' : fields.integer('Zip'),
        'id_sucursal': fields.integer('Id Sucursal'),
        'id_agencia': fields.integer('Id Agencia'),
        'id_correspon': fields.integer('Id Agencia'),
        'correspondent_id': fields.many2one('medical.correspondent','Correspondent'),
        
    }
    
    sql_constraints = [
        
        ('city_zipe_uniq', 'unique(zipe)', 'The zip must be unique.'),
        ('department_name_uniq', 'unique(department_id, name)', 'The Name must be Unique per Department.'),
        
    ]
    
DepartmentCity()


class medical_benefit_type(osv.osv):
    _name = "medical.benefit.type"
    _columns = {
        'code' : fields.char ('Code', size=2, required="True"),
        'name' :fields.char ('Description', size=128 ),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (name)', 'The code must be unique')
    ]
medical_benefit_type ()

class medical_benefit(osv.osv):
    _name = "medical.benefit"
    _columns = {
        'code' : fields.char ('Nro. Obra Social', size=12, required="True"),
        'name' :fields.char ('Beneficiario', size=128 ),
        'benefit_type_id': fields.many2one('medical.benefit.type','Benefit Type'),
        'start_date': fields.date('Start Date', help="Fecha en la cual se ingresaron los datos del beneficio", required="True"),
        'patient_ids': fields.one2many('res.partner','benefit_id','Patients'),###
        'insurance_id': fields.many2one('medical.insurance','Financiadora'),
        #'instution_id': fields.many2one('res.partner','Institution', required="True"),
    }

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name', '')
            code = d.get('code', '')
            #idx = d.get('patient_id', False)
            # if idx:
            #     name = '[%s] %s' % (idx, name)
            if code and name:
                complete_name = '%s - %s' % (code,name)
            else:
                complete_name = code
            return (d['id'], complete_name)
        result = map(_name_get, self.read(cr, user, ids, ['name', 'code'], context))
        return result

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
            
        if not name:
            ids = self.search(cr, user, args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, [('code',operator,name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)

    _sql_constraints = [
        ('code_uniq', 'unique (code,insurance_id)', 'El nro. de Obra Social debe ser único.')
    ]
    def _check_code(self,cr,uid,ids,context=None):
        demo_record = self.browse(cr,uid,ids,context=context)[0]
        code = demo_record.code
        if re.search(r"\s", code):
            raise osv.except_osv(_('Error'),_('El nro. de obra social no puede contener espacios.') )  
        if len(code)!=12:
            raise osv.except_osv(_('Error'),_('El nro. de obra social debe tener 12 dígitos.') )  
        try:
            int(code)
        except:
            raise osv.except_osv(_('Error'),_('El nro. de obra social debe ser de tipo numérico. ') )  
        return True
        
    _constraints = [(_check_code,"Error",['code'] )]
medical_benefit ()

class DepartmentCity(osv.osv):
    
    _name = 'res.department.city'
    _inherit = 'res.department.city'
    _columns = {
        'attention': fields.boolean('Attention')
    }
DepartmentCity()

class medical_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    _patient_age_fnt = lambda self, cr, uid, ids, name, arg, context={}: self._patient_age(cr, uid, ids, name, arg, context)
    _name_get_fnt = lambda self, cr, uid, ids, name, arg, context={}: self.name_get(cr, uid, ids, context)

    def onchange_insurance_number(self, cr, uid, ids, insurance_number, context=None):
        if insurance_number:
            if len(insurance_number)!=15:
                raise osv.except_osv(_('Error'),_('El número de obra social debe tener 15 dígitos.') )  
            benefit = instalation_number[0:12]
            relationship = instalation_number[13:15]
            print benefit
            print relationship
            try:
                int(benefit)
            except Exception, e:
                raise osv.except_osv(_('Error'),_('El número de obra social debe ser numerico con separador /.') )
            try:
                int(relationship)
            except Exception, e:
                raise osv.except_osv(_('Error'),_('El número de obra social debe ser numerico con separador /.') )


            # city = self.pool.get('medical.correspondent').browse(cr, uid, correspondent_id, context)
            # val = {'agency_id':city.agency_id.id,
            #        'subsidiary_id':city.subsidiary_id.id,}
            
            # return {'value': val}
        return {}

    def get_pami_link(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)
        url = 'http://institucional.pami.org.ar/result.php?c=6-2-1-1&beneficio=%s&parent=%s&vm=2'%(this.benefit_id.code,this.relationship_id.code)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
                }

    def onchange_attention_city(self, cr, uid, ids, city_id, context=None):
        if city_id:
            city = self.pool.get('res.department.city').browse(cr, uid, city_id, context)
            val = {'attention_country_rel_id':city.department_id.state_id.country_id.id,
                   'attention_state_rel_id':city.department_id.state_id.id,
                   'attention_department_id':city.department_id.id,}
            return {'value': val}
        return {}

    _columns = {
        'is_patient' : fields.boolean('Patient', help="Check if the partner is a patient"),
        'is_doctor' : fields.boolean('Doctor', help="Check if the partner is a doctor"),
        'is_person' : fields.boolean('Person', help="Check if the partner is a person"),
        'is_institution' : fields.boolean ('Institution', help="Check if the partner is a Medical Center"),
        'lastname' : fields.char('Last Name', size=128, help="Last Name"),
        'document_type': fields.selection([('CI','Cédula de Identidad'),
                                            ('CIB','Cédula de Identidad Brasil'),
                                            ('CIC','Cédula de Identidad Chile'),
                                            ('CIU','Cédula de Identidad Uruguay'),
                                            ('DNI','Documento Nacional de Identidad'),
                                            ('LC','Libreta Cívica'),
                                            ('LE','Libreta de Enrolamiento'),
                                            ('LF','Libreta Femenina'),
                                            ('LM','Libreta Masculina'),
                                            ('PAS','Pasaporte'),
                                            ('RN','Recién Nacido'),
                                            ('SD','Sin Identificación'),
            ],'Document Type'),
        # --- datos paciente
        'age' : fields.function(_patient_age_fnt, method=True, type='char', size=32, string='Patient Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field"),
        'dob' : fields.date ('Date of Birth'),
        'deceased' : fields.boolean ('Deceased', help="Mark if the patient has died"),
        'dod' : fields.datetime ('Date of Death'),
        'insurance': fields.char('Insurance', size=64, required=False, select=True, ),
        'insurance_number': fields.char('Insurance Number', size=15, required=False, select=True, ),
        'dni': fields.char('DNI', size=64, required=True, select=True, help="DNI"),
        'critical_info' : fields.text ('Important disease, allergy or procedures information', help="Write any important information on the patient's disease, surgeries, allergies, ..."),
        'sex' : fields.selection([
            ('m', 'Male'),
            ('f', 'Female'),
        ], 'Sex', select=True),
        'sex' : fields.selection([
            ('M', 'Male'),
            ('F', 'Female'),
        ], 'Sex', select=True),
        'complete_name': fields.function(_name_get_fnt, method=True, type="char", string='Name'),
        'marital_status': fields.selection([('1','Soltero/a'),
                                            ('2','Casado/a'),
                                            ('3','Viudo/a'),
                                            ('4','Separado/a Legal'),
                                            ('5','Separado/a de Hecho'),
                                            ('6','Divorciado/a'),
                                            ('7','Concubino/a'),
                                            ],'Marital Status'),
        'nacionality': fields.selection([('1', 'Argentino'),
                                         ('2', 'Argentino Naturalizado'),
                                         ('3', 'Extranjero'),
                                        ],'Nacionality'),
        'nacionality_id': fields.many2one('res.country','Nationality Country'),
        'cuil': fields.char('CUIL', size=15, required=False, select=True, ),
        'benefit_id': fields.many2one('medical.benefit','Benefit'),
        'relationship_id': fields.many2one('medical.patient.relationship','Relationship'),

        'id_sucursal': fields.integer('Id Sucursal'),
        'id_agencia': fields.integer('Id Agencia'),
        'id_correspon': fields.integer('Id Agencia'),
        'id_pais': fields.integer('Id Pais'),
        'id_beneficio': fields.char ('Id beneficio', size=12,),
        'id_parentesco': fields.char ('Id Parentesco', size=12,),
        'correspondent_id': fields.many2one('medical.correspondent','Correspondent'),
        'agency_id':fields.related('correspondent_id', 'agency_id', type='many2one', relation='medical.agency', string='Agency'),
        'subsidiary_id':fields.related('correspondent_id', 'subsidiary_id', type='many2one', relation='medical.subsidiary', string='Subsidiary'),
        'afjp_id': fields.many2one('medical.afjp','AFJP'),

        'vto_afiliacion': fields.date('Fecha de Vencimineto', help="Fecha de vencimiento para la afiliación"),
        't_formulario': fields.selection([('0', 'Indefinido'),
                                         ('1', 'Ingreso manual en corresponsalía'),
                                         ('2', 'Automático por importación de datos desde el ANSES'),
                                        ],'Tipo de Formulario'),


        # ----- datos medico
        'registration_number': fields.char('National Registration Number', size=64, required=False, select=True, ),
        'state_registration_number': fields.char('State Registration Number', size=64, required=False, select=True, ),
        'speciality' : fields.char('Speciality', size=64, required=False, select=True, ),
        'speciality_id' : fields.many2one ('medical.speciality', 'Speciality', help="Speciality Code"),
        'doctor_start_date': fields.date('Start Date', help="Fecha de inicio del Profesional con el Prestador"),
        'street_number': fields.char('Street Number',size=10),
        'npostal': fields.char('Npostal',size=10),
        'c_profesional': fields.integer('c_profesional'),

        # ------ datos institution - prestadores
        'cuit': fields.char('CUIT', size=15, required=False, select=True, ),
        #'institution_type': fields.integer('Institution Type'),
        'institution_type': fields.selection([('1','Individual'),('2','Institution'),('3','Net')],'Institution Type'),
        'user_name': fields.char('User Name', size=16),
        'nro_sap': fields.char('Nro. SAP', size=16),
        'instalation_number': fields.char('Instalation Number', size=20 ),
        'abbreviation': fields.char('Abbreviation', size=20, help='Abreviatura de la descripción'),
        'head_doctor': fields.boolean('Head Doctor', help="Indica si el prestador es médico de cabecera"),
        'start_date': fields.date('Start Date', help="Fecha a partir de la cual el prestador está habilitado"),
        'end_date': fields.date('End Date', help="Fecha a partir de la cual el prestador deja de está habilitado"),
        'end_reason': fields.char('End Reason', help="Descripción del motivo por el cual el prestador se encuentra dado de baja"),
        'update_date': fields.date('update Date', help="Fecha de actualización del registro de prestador"),
        'attention_point': fields.integer('Attention Point', help="Identificador único de una boca de atención"),
        #'subsidiary_number': fields.integer('Subsidiary Number', help="Identificador único de una sucursal del PAMI."),
        #'subsidiary_id': fields.many2one('medical.subsidiary','Subsidiary', help="Identificador único de una sucursal del PAMI."),
        'module_ids': fields.many2many('medical.module','rel_modulosxprestador','instution_id','module_id','Modules'),
        'prestaciones_ids': fields.one2many('medical.appointment','patient','Prestaciones',ondelete='cascade'),
        'insurance_id':fields.related('benefit_id', 'insurance_id', type='many2one', relation='medical.insurance', string='Financiadora', readonly=True),
        'has_insurance' : fields.boolean ('Tiene financiadora'),
        'attention_city_id' : fields.many2one('res.department.city','Ciudad de Atención', required=False),

        'attention_department_id': fields.related('attention_city_id','department_id', relation='res.state.department', string='Department', type='many2one', readonly=True, store=True),
        'attention_state_rel_id': fields.related('attention_department_id','state_id', relation='res.country.state', string='State', type='many2one', readonly=True),
        'attention_country_rel_id': fields.related('attention_state_rel_id','country_id', relation='res.country', string='Country', type='many2one', readonly=True),

    }
    _sql_constraints = [
        ('benefit_uniq', 'unique (benefit_id, relationship_id)', 'Beneficiario y parentesco deben ser únicos.'),
    ]

    _defaults = {
        
        'street_number':lambda *a: '0',
        't_formulario':lambda *a: '0',
        'phone':lambda *a: '0',
        'id_sucursal':lambda *a: 18,
        'nacionality': '1',
        'nacionality_id': lambda self,cr,uid,context: self.pool.get('res.country').search(cr, uid, [('name','=','Argentina')])[0],
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        'has_insurance':lambda *a: True,

    }
    def _check_dni(self,cr,uid,ids,context=None):
        demo_record = self.browse(cr,uid,ids,context=context)[0]
        partner_ids = self.search(cr, uid, [('dni','=',demo_record.dni),('active','=',True)])
        partner_ids.remove(ids[0])
        if len(partner_ids)>0:
            return False
        return True
        
    _constraints = [(_check_dni,"Ya existe un afiliado cargado con el mismo DNI. ",['dni'] )]

    def name_get(self, cr, user, ids, context={}):
        if not len(ids):
            return []
        def _name_get(d):
            name = d.get('name', '')
            lastname = d.get('lastname', '')
            #idx = d.get('patient_id', False)
            # if idx:
            #     name = '[%s] %s' % (idx, name)
            if lastname and name:
                complete_name = '%s, %s' % (lastname,name)
            else:
                complete_name = name
            return (d['id'], complete_name)
        result = map(_name_get, self.read(cr, user, ids, ['name', 'lastname'], context))
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
                years_months_days = "Fecha de nacimiento no asignada !"

            return years_months_days
        result = {}
        for patient_data in self.browse(cr, uid, ids, context=context):
            result[patient_data.id] = compute_age_from_dates (patient_data.dob, patient_data.deceased, patient_data.dod)
        return result

    def onchange_correspondent_id(self, cr, uid, ids, correspondent_id, context=None):
        if correspondent_id:
            city = self.pool.get('medical.correspondent').browse(cr, uid, correspondent_id, context)
            val = {'agency_id':city.agency_id.id,
                   'subsidiary_id':city.subsidiary_id.id,}
            
            return {'value': val}
        return {}

medical_partner()

class medical_diagnostic(osv.osv):
    _name = "medical.diagnostic"
    _columns = {
        'code' : fields.char ('Code', size=10, required="True"),
        'name' :fields.char ('Description', size=128, required="True" ),
        'frequently_used': fields.boolean('Frequently used'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique')
    ]
medical_diagnostic ()

class medical_appointment_diagnostic(osv.osv):
    _name = "medical.appointment.diagnostic"
    _columns = {
        'diagnostic_id' : fields.many2one ('medical.diagnostic', 'Diagnostic', required=False),
        'appointment_id' : fields.many2one ('medical.appointment', 'Appointment', required=True),
        'm_tipo_diagnostico': fields.selection([('1','Principal'),('2','Secundary')],'Diagnostic Type', required=True),
        'vch_coddiagnostico' : fields.char ('vch_coddiagnostico'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (diagnostic_id,appointment_id)', 'El diagnostico debe ser único por ambulatorio')
    ]
    _defaults = {
        'm_tipo_diagnostico': lambda *a: '1',

    }
medical_appointment_diagnostic ()

class medical_practice(osv.osv):
    _name = "medical.practice"
    _columns = {
        'code' : fields.char ('Code', size=10, required="True"),
        'name' :fields.char ('Description', size=1024, required="True" ),
        'frequently_used': fields.boolean('Frequently used'),
        'consultorio_externo': fields.boolean('Consultorio Externo'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique')
    ]
medical_practice ()

class medical_appointment_practice(osv.osv):
    _name = "medical.appointment.practice"
    _order = "f_fecha_practica asc"

    # def _get_doctor_id(self, cr, uid, context=None):
    #     if context is None:
    #         context = {}
    #     return 1
    def _get_fecha(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for practice in self.browse(cr, uid, ids, context=context):
            cr.execute('''select create_date from medical_appointment_practice where id = %d'''%(practice.id))
            fech = cr.fetchall()
            if fech:
                res[practice.id] = fech[0][0][0:10]
            else: 
                res[practice.id] = '2000-01-01' # si no tiene fecha de creación , asigno una fecha x para registros previos migracion.
        return res

    def _search_fecha(self, cr, uid, obj, name, args, context=None):
        if not args:
            return []
        res = []
        
        if args[0][1]in ('>=','<='):
            cr.execute("""select id from medical_appointment_practice where create_date %s '%s'"""%(args[0][1],args[0][2]))
            res = cr.fetchall()
            
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', map(lambda x:x[0], res))]

    _columns = {
        'practice_id' : fields.many2one ('medical.practice', 'Practice', required=True),
        'appointment_id' : fields.many2one ('medical.appointment', 'Appointment', required=False),
        'vch_codprestacion' : fields.char ('vch_codprestacion'),
        'f_fecha_practica': fields.datetime('Practice Date', required=True),
        'q_cantidad': fields.integer('Practice Quantity', required=True),
        'doctor_id' : fields.many2one ('res.partner', 'Especialista',domain=[('is_doctor', '=', "1")], help="Physician's Name", required=False),
        'c_profesional_solicita' : fields.char ('c_profesional_solicita'),
        'f_create_date': fields.function(_get_fecha,fnct_search=_search_fecha, method=True, type= 'date', string='Fecha Creacion'),  
    }
    _sql_constraints = [
        ('code_uniq', 'unique (practice_id,f_fecha_practica,appointment_id)', 'La práctica debe ser única por horario')
    ]
    _defaults = {
        'q_cantidad': lambda *a: 1,
        #'doctor_id': _get_doctor_id,
    }
    # def _check_code(self,cr,uid,ids,context=None):
    #     demo_record = self.browse(cr,uid,ids,context=context)[0]
    #     fecha = demo_record.f_fecha_practica
    #     try:
    #         int(fecha)
    #     except:
    #         return False
    #     return True
        
    # _constraints = [(_check_code,"La fecha de práctica no puede ser de un mes posterior al actual",['f_fecha_practica'] )]
medical_appointment_practice ()

class medical_appointment (osv.osv):
    _name = "medical.appointment"

    def get_pami_link(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids, context=context)
        url = 'http://institucional.pami.org.ar/result.php?c=6-2-1-1&beneficio=%s&parent=%s&vm=2'%(this.patient.benefit_id.code,this.patient.relationship_id.code)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
                }

    def onchange_care_type (self, cr, uid, ids, care_type, context):
        values={}
        if care_type:
            # appointment_obj = self.pool.get('medical.appointment').browse(cr,uid, appointment_id)
            if care_type not in ('5','6'):
                values['consultorio_externo'] =  True
            else:
                values['consultorio_externo'] =  False
        return {'value': values}
    
    _columns = {
        'doctor' : fields.many2one ('res.partner', 'Physician',domain=[('is_doctor', '=', "1")], help="Physician's Name"),
        'name' : fields.char ('Appointment ID', size=64, readonly=True, required=False),
        'patient' : fields.many2one ('res.partner','Patient', domain=[('is_patient', '=', "1")], help="Patient Name"),
        'insurance_id':fields.related('patient', 'benefit_id', 'insurance_id', type='many2one', relation='medical.insurance', string='Financiadora', readonly=True),
        'appointment_date' : fields.date ('Date'),
        'institution' : fields.many2one ('res.partner', 'Health Center', domain=[('is_institution', '=', "1")], help="Medical Center"),
        #'speciality' : fields.many2one ('medical.speciality', 'Speciality', help="Medical Speciality / Sector"),
        # 'speciality' : fields.char('Speciality', size=64, required=True, select=True, ),
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

        'care_type': fields.selection(CARE_TYPE, 'Care Type'), ##---- Tipo de atencion

        #----------------------- extras migracion
        'c_profesional': fields.integer('c_profesional'),
        'id_modalidad_presta': fields.selection([('1','Afiliado Propio'),('2','Por order de Prestación')],'Modalidad de Prestación'),
        'id_beneficio': fields.char ('Id beneficio', size=12,),
        'id_parentesco': fields.char ('Id Parentesco', size=12,),
        'f_fecha_egreso' : fields.date ('Fecha Finalización'),
        'id_tipo_egreso': fields.selection([
            ('1','Alta Médica Definitiva'),
            ('2','Alta Médica Transitoria'),
            ('3','Traslado a O/ Establecimiento'),
            ('4', 'Defuncion'),
            ('5', 'Retiro Voluntario'),
            ('6', 'Fuga'),
            ('7', 'Internacion Domiciliaria'),
            ('8', 'Otro'),
        ], 'Tipo de Egreso'), ##---- Tipo de atencion

        # 'diagnostic_id' : fields.many2one ('medical.diagnostic', 'Diagnostic'),
        # 'vch_coddiagnostico' : fields.date ('vch_coddiagnostico'),
        #'diagnostic_ids': fields.many2many('medical.diagnostic','diagnosticosxambulatoriopsi','appointment_id','diagnostic_id','Diagnostic'),
        'diagnostic_ids': fields.one2many('medical.appointment.diagnostic','appointment_id','Diagnostic',ondelete='cascade'),
        'practice_ids': fields.one2many('medical.appointment.practice','appointment_id','Practices',ondelete='cascade'),
        'consultorio_externo': fields.boolean('Consultorio Externo'),


    }
    _order = "appointment_date desc"

    _defaults = {
        #'urgency': lambda *a: 'a',
        'name': lambda self, cr, uid, context = None: \
            self.pool.get('ir.sequence').get(cr, uid, 'medical.appointment'),
        'appointment_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'care_type': lambda *a: '1',
        # TODO: arreglar esto
        #'doctor': lambda self, cr, uid, context: self.pool.get('medical.physician')._get_default_doctor(cr, uid, context),
        'state':lambda *a: 'draft',
    }
    _sql_constraints = [
        ('patient_uniq', 'unique (patient,care_type)', 'El ambulatorio debe ser único por paciente y tipo de atención.'),
    ]

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
        for r in self.read(cr, uid, ids, ['care_type', 'appointment_date'], context):
            date = str(r['appointment_date'] or '') +' - '+ CARE_TYPE[int(r['care_type'])-1][1]
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

class medical_init(osv.osv_memory):
    _name = 'medical.init'
    _log_access = True

    def _auto_init(self, cr, context=None):
        ## aca van todos los scripts de base de datos
        sql = ('''update res_department_city set attention=True where municipality in (14001,14002,14003,14004,14005,14006,14007,14008,14009,14010,14011,14012,14013,14014,14015,14016,14017)
                and name in ('ELDORADO','IGUAZU','PUERTO LIBERTAD','PUERTO ESPERANZA','COLONIA WANDA','JARDIN AMERICA','LEANDRO N.ALEM',
                'SANTA RITA','2 DE MAYO','ARISTOBULO DEL VALLE','VILLA SALTO ENCANTADO','25 DE MAYO','SAN JAVIER','SAN VICENTE','EL SOBERBIO',
                'SAN PEDRO','BERNARDO DE IRIGOYEN','OBERA')''')
        cr.execute(sql)
        
        return super(medical_init, self)._auto_init(cr, context=context)

medical_init()
