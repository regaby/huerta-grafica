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
        output += prestador_pool.cuit+';' # CUIT
        output += str(ids[0])+';' # numero de emulacion
        output += time.strftime('%d/%m/%Y')+';' # fecha emulasion
        output += str(this.month).zfill(2)+'-'+str(this.year)[2:4]+';'# mes y año prestacionales
        output += prestador_pool.name+';' # nombre del prestador
        output += str(prestador_pool.institution_type)+';' # tipo de prestador
        output += prestador_pool.user_name+';' # nombre de usuario
        output += prestador_pool.instalation_number + '\n' # nro. de instalacion de efectores

        output += 'RED\n'

        output += prestador_pool.cuit+';' # CUIT
        output += ';;0;' # vacio, vacio, 0
        output += prestador_pool.abbreviation+';' # CUIT
        output += prestador_pool.name+';' # nombre del prestador
        output += '0' +';' # cuit, va 0
        output += prestador_pool.street+';' # calle
        output += '0' +';' # puerta
        output += ';;;' # piso, departamento, npostal
        if prestador_pool.phone:
            output += prestador_pool.phone + '\n' # telefono
        else:
            output += '\n'

        # buscar visitas...
        year = this.year
        month = this.month
        last_day = calendar.monthrange(year,month)
        date_bottom = str(datetime(year, month, 1))[0:10]
        date_top = str(datetime(year, month, last_day[1]))[0:10]
        appointment_ids = self.pool.get('medical.appointment').search(cr, uid, [('appointment_date','>=',date_bottom),('appointment_date','<=',date_top)])

        doctor = []

        for apoint in self.pool.get('medical.appointment').browse(cr, uid, appointment_ids):
            doctor.append(apoint.doctor.id)
            #doctor.update({apoint.doctor.id: apoint.doctor.id})
        # elimino los elementos duplicados
        doctor = list(set(doctor))
        print "doctor..."
        print doctor


        output += 'PROFESIONAL\n'

        for doc in self.pool.get('res.partner').browse(cr, uid, doctor):
            output += ';;;0;'
            output += doc.name + ';' # apellido y nombre
            output += doc.speciality_id.code + ';' # id especialidad
            output += doc.registration_number + ';' # matricula nacional profesional
            output += ';' # matricula provincial, no es obligatoria
            output += 'DNI;0;' # tipo y numero de documento
            output += ';' # cuil, no es obligatorio
            output += doc.street + ';' # calle
            output += '0;' # numero
            output += ';;;' # piso, departamento, npostal
            if doc.phone:
                output += doc.phone + '\n' # telefono
            else:
                output += '\n'

        output += 'PRESTADOR\n'

        output += ';' # vacio
        output += prestador_pool.cuit+';' # CUIT
        output += ';' # matricula nacional del profesional, si no es individual sera null #VER
        output += ';' # vacio
        output += '0' # C_PRESTADOR , poner 0
        output += ';' # n_nro_prestador, nombre de usuario #VER
        output += ';' # n_nro_sap, cod. sap para facturacion #VER






        print output
        return True

        # nom = 'bnf '

        # #
        # for obj in objs:
        #     cr.execute("SELECT ID FROM hr_employee WHERE address_home_id2=%s" % (obj.partner_id.address[0].id))
        #     sql_res = cr.dictfetchone()

        #     if not sql_res and this.type=='interno':
        #         outerr+= "El proveedor %s no tiene agente asociado por address_home_id2.\n"%(obj.partner_id.name)

        #     if len(obj.partner_id.bank_ids)==0:
        #         outerr+= "El proveedor %s no tiene detalle del banco.\n"%(obj.partner_id.name)

        #     # Con al menos un error ya no proceso la salida, solo los errores.
        #     if outerr=="":
        #         if this.type=='interno':
        #             empl = self.pool.get('hr.employee').read(cr, uid, [sql_res['id']], ('licenseno',), context)[0]
        #             output+= '3'+'\t' # Tipo de documento DNI
        #             output+= ('0', empl['licenseno'].replace('.',''))[empl['licenseno']!=False]+'\t' # Numero de documento
        #         else:
        #             output+= '10'+'\t' # Tipo de documento CUIT
        #             output+= obj.partner_id.cuit.replace('-','')+'\t' # Numero de documento
        #         output+= '1'+'\t' # Condicion de ingreso brutos
        #         output+= (('1', '4')[obj.partner_id.title=='MONOTRIBUTISTA'])+'\t' # Condicion de ganancias
        #         output+= (('1', '7')[obj.partner_id.title=='MONOTRIBUTISTA'])+'\t' # Condicion de iva
        #         output+= obj.partner_id.ref+'\t' # Razon social
        #         #
        #         nom = nom+str(obj.partner_id.ref)[4:12]
        #         nom += '.txt'
        #         #
        #         output+= obj.partner_id.address[0].street+'\t' # Calle
        #         output+= (obj.partner_id.address[0].numero or '')+'\t' # Numero de puerta
        #         output+= '0'+'\t'#(obj.partner_id.address[0].unidad_funcional or '')+'\t' # Unidad funcional
        #         output+= ('0', str(obj.partner_id.address[0].zip))[obj.partner_id.address[0].zip!=False]+'\t' # Codigo postal
        #         output+= '' # Nro de ingreso brutos
        #         output+= '\n'

        # if outerr=="":
        #     #filename = 'bnf.txt'
        #     filename = nom.replace(' ','_')

        #     out=base64.encodestring(output.encode('utf-8'))
        #     self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':filename}, context=context)
        # else:
        #     out=base64.encodestring(outerr.encode('utf-8'))
        #     self.write(cr, uid, ids, {'state':'error', 'info':outerr, 'name':''}, context=context)

        # # se agrega return de vista para la version 7.0, antes el return hacia con self.write, pero esto cerraba el wizard
        # view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','efectores.pami')])
        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'efectores.pami',
        #     'name': _('Generar archivo de terceros BENEFICIARIOS'),
        #     'res_id': ids[0],
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'view_id': view_id,
        #     'target': 'new',
        #      'nodestroy': True,
        #      'context': context
        #         }

efectores_pami()
