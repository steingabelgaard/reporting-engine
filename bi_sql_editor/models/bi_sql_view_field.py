# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from openerp import api, fields, models


class BiSQLViewField(models.Model):
    _name = 'bi.sql.view.field'
    _order = 'sequence'

    _TTYPE_SELECTION = [
        ('boolean', 'boolean'),
        ('char', 'char'),
        ('date', 'date'),
        ('datetime', 'datetime'),
        ('float', 'float'),
        ('integer', 'integer'),
        ('many2one', 'many2one'),
        ('selection', 'selection'),
    ]

    _GRAPH_TYPE_SELECTION = [
        ('col', 'Column'),
        ('row', 'Row'),
        ('measure', 'Measure'),
    ]

    # Mapping to guess Odoo field type, from SQL column type
    _SQL_MAPPING = {
        'boolean': 'boolean',
        'bigint': 'integer',
        'integer': 'integer',
        'double precision': 'float',
        'numeric': 'float',
        'text': 'char',
        'character varying': 'char',
        'date': 'datetime',
        'timestamp without time zone': 'datetime',
    }

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

    name = fields.Char(string='Name', required=True, readonly=True)

    sql_type = fields.Char(
        string='SQL Type', required=True, readonly=True,
        help="SQL Type in the database")

    sequence = fields.Integer(string='sequence', required=True, readonly=True)

    bi_sql_view_id = fields.Many2one(
        string='SQL View', comodel_name='bi.sql.view', ondelete='cascade')

    is_index = fields.Boolean(string='Is Index')

    index_name = fields.Char(
        string='Index Name', compute='_compute_index_name')

    graph_type = fields.Selection(
        string='Graph Type', selection=_GRAPH_TYPE_SELECTION)

    field_description = fields.Char(
        string='Field Description', help="This will be used as the name"
        " of the Odoo field, displayed for users")

    ttype = fields.Selection(
        string='Field Type', selection=_TTYPE_SELECTION, help="Type of the"
        " Odoo field that will be created. Let empty if you don't want to"
        " create a new field. If empty, this field will not be displayed"
        " neither available for search or group by function")

    selection = fields.Text(
        string='Selection Options', default='[]',
        help="For 'Selection' Odoo field.\n"
        " List of options, specified as a Python expression defining a list of"
        " (key, label) pairs. For example:"
        " [('blue','Blue'), ('yellow','Yellow')]")

    many2one_model_id = fields.Many2one(
        comodel_name='ir.model', string='Model',
        help="For 'Many2one' Odoo field.\n"
        " Co Model of the field.")

    # Compute Section
    @api.multi
    def _compute_index_name(self):
        for sql_field in self:
            sql_field.index_name = '%s_%s' % (
                sql_field.bi_sql_view_id.view_name, sql_field.name)

    # Overload Section
    @api.multi
    def create(self, vals):
        # guess field description:
        # remove 'x_' replace '_' by ' ' and Capitalize
        if vals['name'][:2] != 'x_':
            field_description = False
        else:
            field_description = re.sub(
                r'\w+', lambda m: m.group(0).capitalize(),
                vals['name'][2:].replace('_', ' '))

        # Guess ttype:
        # Don't execute as simple .get() in the dict to manage
        # correctly the type 'character varying(x)'
        ttype = False
        for k, v in self._SQL_MAPPING.iteritems():
            if k in vals['sql_type']:
                ttype = v

        # Guess many2one_model_id
        many2one_model_id = False
        if vals['sql_type'] == 'integer' and(
                vals['name'][-3:] == '_id' or
                vals['name'][-4:] == '_uid'):
            ttype = 'many2one'
            model_name = self._MODEL_MAPPING.get(vals['name'][2:], '')
            many2one_model_id = self.env['ir.model'].search(
                [('model', '=', model_name)]).id

        vals.update({
            'ttype': ttype,
            'field_description': field_description,
            'many2one_model_id': many2one_model_id,
        })
        return super(BiSQLViewField, self).create(vals)

    # Custom Section
    @api.multi
    def _prepare_model_field(self):
        self.ensure_one()
        return {
            'name': self.name,
            'field_description': self.field_description,
            'model_id': self.bi_sql_view_id.model_id.id,
            'ttype': self.ttype,
            'selection': self.ttype == 'selection' and self.selection or False,
            'relation': self.ttype == 'many2one' and
            self.many2one_model_id.model or False,
        }

    @api.multi
    def _prepare_graph_field(self):
        self.ensure_one()
        res = ''
        if self.graph_type and self.field_description:
            res = """<field name="{}" type="{}" />""".format(
                self.name, self.graph_type)
        return res
