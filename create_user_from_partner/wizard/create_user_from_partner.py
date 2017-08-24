# -*- coding: utf-8 -*-

import time
import datetime
import calendar

from openerp.osv import osv, fields
from openerp.tools.translate import _

class create_user_from_partner(osv.osv_memory):
    _name = 'create.user.from.partner'
    _description = 'create.user.from.partner'
    _columns = {
        'partner_id': fields.many2one('res.partner','Partner', required=True),
        'group_ids': fields.many2many('res.groups','rel_wizard_groups','wizard_id','group_id','Groups'),
        'login': fields.char('Login', required=True),
        'password': fields.char('Password', required=True),
        
    }


    def create_user(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids)[0]
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        groups = []
        for g in wizard.group_ids:
            groups.append(g.id)
        vals = {
            'login': wizard.login,
            'password': wizard.password,
            'partner_id': wizard.partner_id.id,
            'active': True,
            'groups_id': [(6,0,groups)],
            'lang': user.lang,
            'tz': user.tz,
        }
        self.pool.get('res.users').create(cr, uid, vals)
        return {'type': 'ir.actions.act_window_close'}

        

create_user_from_partner()

