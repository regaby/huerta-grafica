# -*- coding: utf-8 -*-
import base64
from openerp.osv import fields,osv
from openerp.tools.translate import _
import time
import calendar
from datetime import datetime, timedelta
import urllib

CARE_TYPE = {'1': 'Atencion Programada a Domicilio',
            '2': 'Urgencias en Domicilio',
            '3': 'Atencion telefonica',
            '4':  'Consultorio Externo',
            '5':  'Hospital de Dia Jornada Simple',
            '6':  'Hospital de Dia Jornada Completa',
            '7':  'Atencion en Jurisdicciones Alejadas',}

class padron_pami(osv.osv_memory):
    """
    Wizard para exportar archivo de efectores PAMI
    """
    _name = "padron.pami"
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
        'create_date_from': fields.date('Fecha Carga desde', required=False),
        'create_date_to': fields.date('Fecha Carga hasta', required=False),
        'doctor_id': fields.many2one('res.partner', 'Profesional', domain=[('is_doctor','=',True)]),
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

        # buscar visitas...
        year = this.year
        month = this.month
        last_day = calendar.monthrange(year,month)
        date_bottom = str(datetime(year, month, 1))[0:10]
        date_top = str(datetime(year, month, last_day[1]))[0:10]
        
        prestador_id = self.pool.get('res.partner').search(cr, uid, [('is_institution','=',True)])
        prestador_pool = self.pool.get('res.partner').browse(cr, uid, prestador_id, context)
        output += prestador_pool.cuit +';' # CUIT
        numero_emulacion = str(ids[0])
        fecha_emulacion = time.strftime('%d_%m_%Y')
        periodo_emulacion = str(this.month).zfill(2)+'-'+str(this.year)[2:4]
        output += numero_emulacion+';' # numero de emulacion
        output += datetime.strptime(date_top, '%Y-%m-%d').strftime('%d/%m/%Y')+';' # fecha emulasion

        output += periodo_emulacion + ';'# mes y año prestacionales
        output += prestador_pool.name+';' # nombre del prestador
        output += str(prestador_pool.institution_type)+';' # tipo de prestador
        output += prestador_pool.user_name+';' # nombre de usuario
        output += prestador_pool.instalation_number + '\n' # nro. de instalacion de efectores

        
        # month = int(month) + 1
        # if month == 13:
        #     month = 1
        #     year = year +1
        # date_top = str(year)+'-'+str(month)+'-01'
        args = [('f_fecha_practica','>=',date_bottom),('f_fecha_practica','<=',date_top)]

        sql = """select pat.name,  mb.code beneficio, mpr.code relacion
                from medical_prestaciones_by_pat_view  ma
                join res_partner pat on (ma.patient=pat.id)
                join medical_benefit mb on (pat.benefit_id=mb.id)
                join medical_patient_relationship mpr on (pat.relationship_id=mpr.id)
                where year='%s-%s'
        """%(year,str(month).zfill(2))
        cr.execute(sql)
        print cr.query
        result = cr.dictfetchall()
        for r in result:
            response = urllib.urlopen('http://institucional.pami.org.ar/result.php?c=6-2-1-1&beneficio=%s&parent=%s'%(r['beneficio'],r['relacion']))
            headers = response.info()
            data = response.read()
            if 'RED PREVENIR' in data:
                print 'exito'
            else:
                print 'fallo'
                outerr+= "Afiliado: %s no esta dado de alta en el padron de PAMI\n"%(r['name'])



        if outerr=="":
            msj = 'Padron correcto'
            out=base64.encodestring(output.encode('utf-8'))
            self.write(cr, uid, ids, {'state':'get', 
                'info2': msj}, context=context)
        else:
            out=base64.encodestring(outerr.encode('utf-8'))
            self.write(cr, uid, ids, {'state':'error', 'info':outerr, 'name':''}, context=context)

        # se agrega return de vista para la version 7.0, antes el return hacia con self.write, pero esto cerraba el wizard
        view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','padron.pami')])
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'padron.pami',
            'name': _('Generar archivo de terceros BENEFICIARIOS'),
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
             'nodestroy': True,
             'context': context
                }

padron_pami()
