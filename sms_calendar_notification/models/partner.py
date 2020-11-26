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
import calendar

from openerp.osv import fields, osv
from openerp.tools.translate import _

from lxml import etree
import re

class res_partner (osv.osv):
    _inherit = "res.partner"

    _columns = {
        'sms_notification': fields.boolean('Enviar Turno por SMS'),

    }
    _defaults = {
        'sms_notification': True,
    }

res_partner()
