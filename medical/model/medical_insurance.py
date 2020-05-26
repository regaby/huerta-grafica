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

# DEBUG MODE -- DELETE ME !
# import pdb
class medical_insurance (osv.osv):
    _name = "medical.insurance"
    _columns = {
        'name' :fields.char ('Nombre', size=128, required="True"),
        'code' : fields.char ('Código', size=128, required="True"),
        'description': fields.text ('Descripción'),
        'size': fields.integer('Longitud Nro. Obra Social'),
        'has_relationship': fields.boolean('Tiene parentesco?'),
        'has_code': fields.boolean('Tiene Nro. de obra social?'),
        'is_particular': fields.boolean('Es particular?'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code must be unique'),
        ('name_uniq', 'unique (name)', 'The name must be unique')
    ]
    _defaults = {
        'has_code': True,
    }
medical_insurance ()
