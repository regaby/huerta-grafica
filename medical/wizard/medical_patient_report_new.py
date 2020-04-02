# -*- coding: utf-8 -*-

import time
import datetime
import calendar

from openerp.osv import osv, fields
from openerp.tools.translate import _

CARE_TYPE = [
    ('1', 'Atención Programada a Domicilio'),
    ('2', 'Urgencias en Domicilio'),
    ('3', 'Atención telefónica'),
    ('4', 'Consultorio Externo'),
    ('5', 'Hospital de Dia Jornada Simple'),
    ('6', 'Hospital de Dia Jornada Completa'),
    ('7', 'Atención en Jurisdicciónes Alejadas'),
]

class medical_patient_report_new(osv.osv_memory):
    _name = 'medical.patient.report.new'
    _description = 'medical.patient.report.new'
    _columns = {
        'date_from': fields.date('Fecha desde', required=True),
        'date_to': fields.date('Fecha hasta', required=True),
        'care_type': fields.selection(CARE_TYPE, 'Tipo de atención', required=True), ##---- Tipo de atencion
        'insurance_id': fields.many2one('medical.insurance', 'Financiadora'),
        'psiquiatria': fields.boolean('Psiquiatría'),
        'psicologia': fields.boolean('Psicología'),
        'psicopedadogia': fields.boolean('Psicopedadogía'),
    }

    def _get_inicio_mes(self, cr, uid, context=None):
        date = datetime.datetime.now()
        return str(date.replace(day=1))[0:10]

    def _get_fin_mes(self, cr, uid, context=None):
        date = datetime.datetime.now()
        return str(date.replace(day=calendar.monthrange(date.year, date.month)[1]))[0:10]

    _defaults = {
        'date_from': _get_inicio_mes,
        'date_to': _get_fin_mes,
    }



    def print_report(self, cr, uid, ids, context=None):
        #wizard = self.browse(cr, uid, ids)[0]
        datas = {
            'ids': [],
            'model': 'medical.patient.report.new',
            'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'medical_pacientes_report',
            'datas': datas,
        }



medical_patient_report_new()

