# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from openerp import api, fields, models

from .bi_sql_field import _TTYPE_SELECTION


class BiSQLFieldWizard(models.TransientModel):
    _name = 'bi.sql.field.wizard'

    # Mapping to try to guess most common many2one model, based on field name
    _MODEL_MAPPING = {
        # Base Model
        'partner_id': 'res.partner',
        'user_id': 'res.users',
        'uid': 'res.users',
        # Product Model
        'product_id': 'product.product',
        'product_tmpl_id': 'product.template',
        'uom_id': 'product.uom',
        'categ_id': 'product.category',
        # Account Model
        'account_id': 'account.account',
        'invoice_id': 'account.invoice',
        'journal_id': 'account.journal',
        'period_id': 'account.period',
    }

    _SQL_MAPPING = {
        'boolean': 'boolean',
        'integer': 'integer',
        'double precision': 'float',
        'numeric': 'float',
        'character varying': 'char',
        'date': 'datetime',
        'timestamp without time zone': 'datetime',
    }

    # Column Section
    name = fields.Char(string='Name', required=True, readonly=True)

    sql_type = fields.Char(
        string='SQL Type', readonly=True,
        help="SQL Type in the database")

    field_description = fields.Char(string='Field Description', required=True)

    bi_sql_field_id = fields.Many2one(comodel_name='bi.sql.field')

    ttype = fields.Selection(
        string='Field Type', selection=_TTYPE_SELECTION, required=True)

    selection = fields.Char(
        string='Selection Options', default='[]',
        help="List of options for a selection"
        " field, specified as a Python expression defining a list of"
        " (key, label) pairs. For example:"
        " [('blue','Blue'),('yellow','Yellow')]")

    many2one_model_id = fields.Many2one(
        comodel_name='ir.model', string='Model',
        help="Model for a Many2one field")

    # Overload Section
    @api.model
    def default_get(self, fields):
        sql_field_obj = self.env['bi.sql.field']
        res = super(BiSQLFieldWizard, self).default_get(fields)

        sql_field = sql_field_obj.browse(self.env.context['active_id'])

        res.update(self._prepare_wizard_field(sql_field))
        return res

    # Action Section
    @api.multi
    def button_create_field(self):
        self.ensure_one()
        vals = self._prepare_model_field()
        vals['state'] = 'base'
        field_id = self.env['ir.model.fields'].create(vals)
        self.bi_sql_field_id.field_id = field_id.id

    # Custom Section
    def _guess_model_id(self, sql_field):
        model_name = self._MODEL_MAPPING.get(sql_field.name, '')
        return self.env['ir.model'].search([('model', '=', model_name)]).id

    def _guess_type(self, sql_field):
        # Don't execute as simple .get() in the dict to manage
        # correctly the type 'character varying(x)'
        for k, v in self._SQL_MAPPING.iteritems():
            if k in sql_field.sql_type:
                return v
        return False

    @api.model
    def _prepare_wizard_field(self, sql_field):
        # Camel case the name
        field_description = re.sub(
            r'\w+', lambda m: m.group(0).capitalize(),
            sql_field.name.replace('_', ' '))
        ttype = self._guess_type(sql_field)
        many2one_model_id = False
        if sql_field.sql_type == 'integer' and(
                sql_field.name[-3:] == '_id' or
                sql_field.name[-4:] == '_uid'):
            ttype = 'many2one'
            many2one_model_id = self._guess_model_id(sql_field)
        # TODO FIXME set 'state' == 'manual'
        # AND RELOAD REGISTRY
        return {
            'field_description': field_description,
            'name': sql_field.name,
            'sql_type': sql_field.sql_type,
            'ttype': ttype,
            'many2one_model_id': many2one_model_id,
            'bi_sql_field_id': sql_field.id,
        }

    @api.multi
    def _prepare_model_field(self):
        self.ensure_one()
        return {
            'name': self.name,
            'field_description': self.field_description,
            'model_id': self.bi_sql_field_id.bi_sql_view_id.model_id.id,
            'ttype': self.ttype,
            'selection': self.ttype == 'selection' and self.selection or False,
            'relation': self.many2one_model_id.name,
        }
