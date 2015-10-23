# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta

from openerp.osv import osv, fields
from openerp.tools.translate import _

class medical_patient_report_wizard(osv.osv_memory):
    _name = 'medical.patient.report.wizard'
    _description = 'medical.patient.report.wizard'
    _columns = {
        'date_from': fields.date('Fecha desde', required=True),
        'date_to': fields.date('Fecha hasta', required=True),
        'doctor_id': fields.many2one('res.partner', 'Doctor', domain=[('is_doctor','=',True)]),
        'patient_id': fields.many2one('res.partner', 'Patient', domain=[('is_patient','=',True)]),
        #'product_id': fields.many2one('product.product', 'Producto'),
    }
    _defaults = {
         'date_from': lambda *a: (datetime.now()-timedelta(days=10)).strftime('%Y-%m-%d'),
         'date_to': lambda *a: (datetime.now()).strftime('%Y-%m-%d'),

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
            'report_name': 'medical_patient_report',
            'datas': datas,
        }
        
        

medical_patient_report_wizard()

