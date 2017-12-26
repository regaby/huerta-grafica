# -*- coding: utf-8 -*-

import time
import datetime
import calendar

from openerp.osv import osv, fields
from openerp.tools.translate import _

class medical_patient_report_wizard(osv.osv_memory):
    _name = 'medical.patient.report.wizard'
    _description = 'medical.patient.report.wizard'
    _columns = {
        'date_from': fields.date('Fecha desde', required=True),
        'date_to': fields.date('Fecha hasta', required=True),
        'doctor_id': fields.many2one('res.partner', 'Profesional', domain=[('is_doctor','=',True)]),
        'patient_id': fields.many2one('res.partner', 'Patient', domain=[('is_patient','=',True)]),
        'city_id' : fields.many2one('res.department.city','Ciudad'),
        'mostrar_pacientes': fields.boolean('Mostrar detalle de pacientes?'),
        #'product_id': fields.many2one('product.product', 'Producto'),
        'year': fields.char('Periodo',required=True)
    }

    def _get_inicio_mes(self, cr, uid, context=None):
        date = datetime.datetime.now()
        return str(date.replace(day = 1))[0:10]

    def _get_fin_mes(self, cr, uid, context=None):
        date = datetime.datetime.now()
        return str(date.replace(day = calendar.monthrange(date.year, date.month)[1]))[0:10]

    _defaults = {
         #'date_from': lambda *a: (datetime.now()-timedelta(days=10)).strftime('%Y-%m-%d'),
         #'date_to': lambda *a: (datetime.now()).strftime('%Y-%m-%d'),
         'date_from': _get_inicio_mes,
         'date_to': _get_fin_mes,
         'mostrar_pacientes': lambda *a: False,

    }

    

    def print_report(self, cr, uid, ids, context=None):
        #wizard = self.browse(cr, uid, ids)[0]
        datas = {
             'ids': [],
             'model': 'medical.patient.report.wizard',
             'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'medical_prestaciones_by_doctor_report',
            'datas': datas,
        }
        
        

medical_patient_report_wizard()

