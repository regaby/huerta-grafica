# -*- coding: utf-8 -*-
import base64
from openerp.osv import fields,osv
from openerp.tools.translate import _
import time
import calendar
from datetime import datetime

class efectores_pami(osv.osv_memory):
    """
    Wizard para exportar archivo de efectores PAMI
    """
    _name = "efectores.pami"
    _description = "Generar archivo efectores PAMI"
    _columns = {
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 16, readonly=True),
        
        'info': fields.text('Info'),
        'info2': fields.text('Info'),
        'state': fields.selection( ( ('choose','choose'),
                                     ('get','get'),
                                     ('done','done'),
                                     ('error','error'),
                                 ) ),
        'month': fields.selection([(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')], 'Mes', required=True),
        'year': fields.integer('Año', required=True),
        }
    _defaults = {
         'month': lambda *a: time.gmtime()[1],
         'year': lambda *a: time.gmtime()[0],
         'state': lambda *a: 'choose',
         }
    
    def generate_file(self,cr,uid,ids,context={}):

        this = self.browse(cr, uid, ids)[0]

        # objs = self.pool.get('account.voucher').browse(cr, uid, context['active_ids'], context)
        output = 'CABECERA\n'
        outerr = ''
        ## CABECERA
        
        prestador_id = self.pool.get('res.partner').search(cr, uid, [('is_institution','=',True)])
        prestador_pool = self.pool.get('res.partner').browse(cr, uid, prestador_id, context)
        output += prestador_pool.cuit +';' # CUIT
        numero_emulacion = str(ids[0])
        fecha_emulacion = time.strftime('%d_%m_%Y')
        periodo_emulacion = str(this.month).zfill(2)+'-'+str(this.year)[2:4]
        output += numero_emulacion+';' # numero de emulacion
        output += time.strftime('%d/%m/%Y')+';' # fecha emulasion

        output += periodo_emulacion + ';'# mes y año prestacionales
        output += prestador_pool.name+';' # nombre del prestador
        output += str(prestador_pool.institution_type)+';' # tipo de prestador
        output += prestador_pool.user_name+';' # nombre de usuario
        output += prestador_pool.instalation_number + '\n' # nro. de instalacion de efectores

        # buscar visitas...
        year = this.year
        month = this.month
        last_day = calendar.monthrange(year,month)
        date_bottom = str(datetime(year, month, 1))[0:10]
        date_top = str(datetime(year, month, last_day[1]))[0:10]
        appointment_ids = self.pool.get('medical.appointment.practice').search(cr, uid, [('f_fecha_practica','>=',date_bottom),('f_fecha_practica','<=',date_top)])

        doctors = []
        patients = []

        for apoint in self.pool.get('medical.appointment.practice').browse(cr, uid, appointment_ids):
            doctors.append(apoint.appointment_id.doctor.id)
            patients.append(apoint.appointment_id.patient.id)
            #doctor.update({apoint.doctor.id: apoint.doctor.id})
        # elimino los elementos duplicados
        doctors = list(set(doctors))
        patients = list(set(patients))


        output += 'PROFESIONAL\n'

        for doc in self.pool.get('res.partner').browse(cr, uid, doctors):
            output += ';;;0;'
            output += doc.name + ';' # apellido y nombre
            output += doc.speciality_id.code + ';' # id especialidad
            output += doc.registration_number + ';' # matricula nacional profesional
            if doc.state_registration_number:
                output += doc.state_registration_number + ';'
            else:
                output += ';' # matricula provincial, no es obligatoria
            output += doc.document_type + ';' + doc.dni +';' # tipo y numero de documento
            if doc.cuil:
                output += doc.cuil + ';' # cuil
            else:
                output += ';'
            if doc.street:
                output += doc.street + ';' # calle
            else:
                output += 'SIN SUMINISTRAR;' # calle
            if doc.street_number:
                output += doc.street_number+';'
            else:
                output += '0;' # puerta
            output += ';;' # piso, departamento
            if doc.city_id:
                output += str(doc.city_id.zip_city) + ';' # npostal
            else:
                output += ';'
            if doc.phone:
                output += doc.phone + '\n' # telefono
            else:
                output += '\n'

        output += 'PRESTADOR\n'

        output += ';' # vacio
        output += prestador_pool.cuit +';' # CUIT
        output += ';' # matricula nacional del profesional, si no es individual sera null #VER
        output += ';' # vacio
        output += '0;' # C_PRESTADOR , poner 0
        if prestador_pool.user_name:
            output += prestador_pool.user_name + ';' # n_nro_prestador, nombre de usuario
        else:
            output += ';' 
        if prestador_pool.nro_sap:
            output += prestador_pool.nro_sap + ';' # nro_sap
        else:
            output += ';' 
        output += str(prestador_pool.institution_type)+';' # tipo de prestador
        output += ';' # tabla iva
        if prestador_pool.head_doctor: # medico de cabecera
            output += '1;' # el prestador es medico de cabecera
        else:
            output += '0;' # el prestador no es medico de cabecera
        output += prestador_pool.email + ';'
        output += datetime.strptime(prestador_pool.start_date, '%Y-%m-%d').strftime('%d/%m/%Y') +';' # fecha de alta

        if prestador_pool.end_date:
            #output += prestador_pool.end_date.strftime('%d/%m/%Y')+';' # fecha de baja
            output += datetime.strptime(prestador_pool.end_date, '%Y-%m-%d').strftime('%d/%m/%Y') +';' # fecha de alta
            output += prestador_pool.end_reason
        else:
            output += ';;'
        if prestador_pool.update_date:
            #output += prestador_pool.update_date.strftime('%d/%m/%Y')+';' # fecha de actualización
            output += datetime.strptime(prestador_pool.update_date, '%Y-%m-%d').strftime('%d/%m/%Y') +';' # fecha de actualizacion
        else:
            output += ';' 
        output += '0;0;0;' # cuit, profesional, id_red
        output += prestador_pool.name + ';' # nombre del prestador institución
        output += prestador_pool.street+';' # calle
        if prestador_pool.street_number:
            output += prestador_pool.street_number+';'
        else:
            output += '0;' # puerta
        output += ';;' # piso, departamento
        if prestador_pool.city_id:
            output += str(prestador_pool.city_id.zip_city) + ';' # npostal
        else:
            output += ';'
        if prestador_pool.phone:
            output += prestador_pool.phone + ';' # telefono 
        else:
            output += ';'
        if prestador_pool.instalation_number:
            output += prestador_pool.instalation_number + '\n' # identificador unido de nstalacion de BD para el prestador
        else:
            output += '\n'


        output += 'REL_PROFESIONALESXPRESTADOR\n'

        for doc in self.pool.get('res.partner').browse(cr, uid, doctors):
            output += ';' # vacio
            output += prestador_pool.cuit +';' # CUIT
            if doc.registration_number=='0':
                outerr+= _('El numero de matricula del especialista %s debe ser diferente a 0.\n'%(doc.name))
            output += doc.registration_number + ';' # matricula nacional profesional
            output += '0;0;'
            if doc.start_date:
                output += datetime.strptime(doc.start_date, '%Y-%m-%d').strftime('%d/%m/%Y') +'\n' # fecha de alta
            else:
                output += '\n'

        output += 'BOCA_ATENCION\n'
        output += ';' # vacio
        output += prestador_pool.cuit +';' # CUIT
        output += ';0;' # vacio + 0
        output += str(prestador_pool.attention_point) + ';' # boca de atencion
        #output += str(prestador_pool.subsidiary_number) + ';' # numero sucursal PAMI
        if prestador_pool.id_sucursal:
            output += str(prestador_pool.id_sucursal) + ';' # numero sucursal PAMI
        else:
            outerr+= "El prestador %s no tiene sucursal asignada.\n"%(prestador_pool.complete_name)
        output += prestador_pool.street+';' # calle
        if prestador_pool.street_number:
            output += prestador_pool.street_number+';'
        else:
            output += '0;' # puerta
        output += ';;' # piso, departamento
        if prestador_pool.city_id:
            output += str(prestador_pool.city_id.zip_city) + ';' # npostal
        else:
            output += ';'
        if prestador_pool.phone:
            output += prestador_pool.phone + '\n' # telefono 
        else:
            output += '\n'

        output += 'REL_MODULOSXPRESTADOR\n'
        for module in prestador_pool.module_ids:
            output += ';' # vacio
            output += prestador_pool.cuit +';' # CUIT
            output += ';' # vacio
            output += '0;' # C_PRESTADOR , poner 0
            output += module.code + ';' 
            if module.start_date:
                output += module.start_date + '\n' # fecha de alta de la relación entre modulo y prestador
            else:
                output += '\n'




        # output += 'REL_PRESTADORESXRED\n'
        # output += prestador_pool.cuit +';' # CUIT
        # output += prestador_pool.cuit +';' # CUIT
        # output += ';0;0;\n' # vacio + 0 + 0

        output += 'BENEFICIO\n'
        for pat in self.pool.get('res.partner').browse(cr, uid, patients):
            output += ';;;' # 3 vacios
            if pat.benefit_id:
                output += pat.benefit_id.code +';' # id beneficio
                if pat.benefit_id.benefit_type_id:
                    output += pat.benefit_id.benefit_type_id.code +';' # id tipo beneficio
                else:
                    output += ';'
                if pat.benefit_id.name:
                    output += pat.benefit_id.name +';' # denominacion beneficio
                else:
                    output += ';'
                output += '1;' # ni_alta_por_presta siempre es 1
                if pat.benefit_id.start_date:
                    output += datetime.strptime(pat.benefit_id.start_date, '%Y-%m-%d').strftime('%d/%m/%Y') +'\n' # fecha de alta
                else:
                    outerr+= "El beneficio del afiliado %s no tiene fecha de alta.\n"%(pat.complete_name)
            else:
                outerr+= "El afiliado %s no tiene beneficio relacionado.\n"%(pat.complete_name)


        output += 'AFILIADO\n'
        for pat in self.pool.get('res.partner').browse(cr, uid, patients):
            output += pat.name + ';' # nombre y apellido de la persona
            if pat.document_type:
                output += pat.document_type + ';' # tipo de documento
            else:
                output += 'DNI'
            output += pat.dni + ';' # nro de documento
            if pat.marital_status: 
                output += pat.marital_status + ';' 
            else: 
                output += ';' # estado civil
            if pat.nacionality:
                output += pat.nacionality + ';' # nacionalidad
            else:
                output += ';' 
            if pat.nacionality_id:
                output += pat.nacionality_id.code + ';' # nacionalidad pais
            else:
                output += ';' 
            if pat.street:
                output += pat.street + ';' # cale
            else:
                output += ';' 
            if pat.street_number:
                output += pat.street_number+';'
            else:
                output += '0;' # puerta
            output += ';;' # piso, departamento
            if pat.city_id:
                output += str(pat.city_id.zip_city) + ';' # npostal
            else:
                output += ';'
            if pat.phone:
                output += pat.phone + ';' # telefono
            else:
                output += ';'
            if pat.dob:
                try:
                    output += datetime.strptime(pat.dob, '%Y-%m-%d').strftime('%d/%m/%Y') +';' # fecha de nacimiento
                except Exception, e:
                    outerr+= 'La fecha de nacimiento del paciente %s es previo a 1900.\n'%(pat.name) 
            else:
                outerr+= "El afiliado %s no tiene fecha de nacimiento.\n"%(pat.complete_name)
            if pat.sex:
                output += pat.sex + ';' # sexo
            else:
                outerr+= "El afiliado %s no tiene el campo sexo asignado.\n"%(pat.complete_name)
            if pat.cuil:
                output += pat.cuil + ';' # cuil
            else:
                output += ';'
            if pat.cuit:
                output += pat.cuit + ';' # cuit
            else:
                output += ';' 
            # if pat.insurance_number:
            #     output += pat.insurance_number[0:12] + ';' # id beneficio
            # else:
            #     outerr+= "El afiliado %s no tiene número de obra social.\n"%(pat.complete_name)
            if pat.benefit_id.code:
                output += pat.benefit_id.code + ';' # id beneficio
            else:
                outerr+= "El afiliado %s no tiene código de beneficio relacionado.\n"%(pat.complete_name)
            if pat.relationship_id:
                output += pat.relationship_id.code + ';' # id parentesco
            else:
                outerr+= "El afiliado %s no tiene el campo parentesco asignado.\n"%(pat.complete_name)
            output += ';;;;;;;\n' # id_sucursal, id_agencia, id_corresponsalia, id_afjp, vto_afiliado, f_formulario, fecha_baja, codigo_baja
        output += 'PRESTACIONES\n'
        
        for apoint in self.pool.get('medical.appointment.practice').browse(cr, uid, appointment_ids):
            output += 'AMBULATORIOPSI\n'
            output += ';;'
            output += apoint.appointment_id.doctor.registration_number + ';' # matricula nacional del profesional
            output += '0;0;0;' # c_ambulatorio, id_red, c_prestador
            output += str(prestador_pool.attention_point) + ';' # boca de atencion
            output += '0;' # c_profesional
            output += datetime.strptime(apoint.f_fecha_practica, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y  %H:%M') +';' # fecha de atencion
            output += ';' # d_estado
            output += ';' # d_motivo_rechazo
            output += apoint.appointment_id.id_modalidad_presta + ';' # id_modalidad_presta
            output += ';' # n_nro_orden
            output += apoint.appointment_id.care_type + ';' # id_tipo_atencion 
            output += apoint.appointment_id.patient.benefit_id.code + ';' # id_beneficio
            output += apoint.appointment_id.patient.relationship_id.code + ';' # id parentesco
            if apoint.appointment_id.f_fecha_egreso:
                output += datetime.strptime(apoint.appointment_id.f_fecha_egreso, '%Y-%m-%d').strftime('%d/%m/%Y') +';' # fecha de egreso
            else:
                output += ';' 
            if apoint.appointment_id.id_tipo_egreso:
                output += apoint.appointment_id.id_tipo_egreso + ';'
            else:
                output += ';' 
            if apoint.appointment_id.comments:
                output += apoint.appointment_id.comments + '\n'
            else:
                output += '\n' 
            output += 'REL_DIAGNOSTICOSXAMBULATORIOPSI\n'
            for diagnostic in apoint.appointment_id.diagnostic_ids:
                output += ';;;'
                output += '0;' # c_ambulatorio
                output += '1;' # ni_coddiagno
                output += diagnostic.diagnostic_id.code + ';' # vch_coddiagnostico
                output += diagnostic.m_tipo_diagnostico + '\n' # m_tipo_diagnostico
                #output += '1\n'

            output += 'REL_PRACTICASREALIZADASXAMBULATORIOPSI\n'
            #for practice in apoint.practice_ids:
            output += ';;;'
            output += '0;' # c_ambulatorio
            output += '1;' # ni_codpresta
            output += apoint.practice_id.code + ';' # vch_codprestacion
            output += datetime.strptime(apoint.f_fecha_practica, '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y  %H:%M') + ' 00:00' +';' # fecha que se realizó la práctica
            output += str(apoint.q_cantidad) + ';' # cantidad de practicas realizadas
            output += '0;' # c_prestador_solicita
            output += '0\n' # c_profesional_solicita

            output += 'MEDICACIONXAMBULATORIOPSI\n'
            output += 'FIN AMBULATORIOPSI\n'


        #print output
        #print outerr

        MONTH = {1: 'Ene',
                2: 'Feb',
                3: 'Mar',
                4: 'Abr',
                5: 'May',
                6: 'Jun',
                7: 'Jul',
                8: 'Ago',
                9: 'Sep',
                10: 'Oct',
                11: 'Nov',
                12: 'Dic',}

        if outerr=="":
            #filename = 'bnf.txt'
            #filename = 'efectores_%s_%s.txt' % (numero_emulacion,fecha_emulacion)
            filename = '%s_%s.txt' % (MONTH[this.month],this.year)

            #30-69806560-1_05_09_2015_08-2015_216_UP3069806560100_jo432
            msj = 'Se han generado %s prestaciones'%(len(appointment_ids))
            out=base64.encodestring(output.encode('utf-8'))
            self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':filename,
                'info2': msj}, context=context)
        else:
            out=base64.encodestring(outerr.encode('utf-8'))
            self.write(cr, uid, ids, {'state':'error', 'info':outerr, 'name':''}, context=context)

        # se agrega return de vista para la version 7.0, antes el return hacia con self.write, pero esto cerraba el wizard
        view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','efectores.pami')])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'efectores.pami',
            'name': _('Generar archivo de terceros BENEFICIARIOS'),
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
             'nodestroy': True,
             'context': context
                }

efectores_pami()
