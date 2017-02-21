# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from psycopg2 import ProgrammingError

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.exceptions import Warning
from openerp.modules.registry import RegistryManager

_STATE_SELECTION = [
    ('draft', 'Draft'),
    ('sql_view_created', 'SQL View Created'),
    ('registry_updated', 'Registry Updated'),
    ('ui_created', 'UI Created'),
]

_logger = logging.getLogger(__name__)


class BiSQLView(models.Model):
    _name = 'bi.sql.view'

    name = fields.Char(string='Name', required=True)

    technical_name = fields.Char(
        string='Technical Name', required=True, default='x_',
        help="Name of the SQL view. Should start with 'x_' and have correct"
        "syntax. For more information, see https://www.postgresql.org/"
        "docs/current/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS")

    is_materialized = fields.Boolean(
        string='Is Materialized View', default=True, readonly=True,
        states={'draft': [('readonly', False)]})

    materialized_text = fields.Char(
        compute='_compute_materialized_text', store=True)

    size = fields.Char(
        string='Database Size', readonly=True,
        help="Size of the materialized view and its indexes")

    state = fields.Selection(
        string='State', required=True, selection=_STATE_SELECTION,
        default='draft')

    sql_request = fields.Text(
        string='SQL Request', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        help="SQL Request that will be inserted as the view. Take care to :\n"
        " * set a name for all your selected fields, specially if you use"
        " SQL function (like EXTRACT, ...);\n"
        " * Do not use 'SELECT *' or 'SELECT table.*';\n"
        " * do not end your request by ';'\n"
        " * Begin your request by 'SELECT row_number() OVER () AS id';\n"
        " * prefix your column by 'x_';")

    bi_sql_field_ids = fields.One2many(
        string='SQL Fields', comodel_name='bi.sql.field',
        inverse_name='bi_sql_view_id')

    model_id = fields.Many2one(
        string='Odoo Model', comodel_name='ir.model', readonly=True)

    view_id = fields.Many2one(
        string='Odoo View', comodel_name='ir.ui.view', readonly=True)

    action_id = fields.Many2one(
        string='Odoo Action', comodel_name='ir.actions.act_window',
        readonly=True)

    menu_id = fields.Many2one(
        string='Odoo Menu', comodel_name='ir.ui.menu', readonly=True)

    cron_id = fields.Many2one(
        string='Odoo Cron', comodel_name='ir.cron', readonly=True,
        help="Cron Task that will refresh the materialized view")

    # Compute Section
    @api.multi
    @api.depends('is_materialized')
    def _compute_materialized_text(self):
        for sql_view in self:
            sql_view.materialized_text =\
                self.is_materialized and 'MATERIALIZED' or ''

    # Overload Section
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update({
            'name': _('%s (Copy)') % (self.name),
            'technical_name': '%s_copy' % (self.technical_name),
        })
        return super(BiSQLView, self).copy(default=default)

    # Action Section
    @api.multi
    def button_set_draft(self):
        self._drop_index()
        self._drop_view()
        self.bi_sql_field_ids.unlink()
        self.model_id.unlink()
        self.view_id.unlink()
        self.action_id.unlink()
        self.menu_id.unlink()
        self.cron_id.unlink()
        self.write({'state': 'draft'})

    @api.multi
    def button_create_sql_view(self):
        if any([x.state != 'draft' for x in self]):
            raise _("You can only process this action on draft items")
        self._create_view()
        self._create_model()
        self._refresh_schema()
        if self.is_materialized:
            self.cron_id = self.env['ir.cron'].create(
                self._prepare_cron()).id
        self.write({'state': 'sql_view_created'})

    @api.multi
    def button_update_registry(self):
        RegistryManager.new(self._cr.dbname, update_module=True)
        RegistryManager.signal_registry_change(self._cr.dbname)
        self._create_index()
        self.write({'state': 'registry_updated'})

    @api.multi
    def button_create_ui(self):
        self.view_id = self.env['ir.ui.view'].create(
            self._prepare_view()).id
        self.action_id = self.env['ir.actions.act_window'].create(
            self._prepare_action()).id
        self.menu_id = self.env['ir.ui.menu'].create(
            self._prepare_menu()).id
        self.write({'state': 'ui_created'})

    @api.multi
    def button_refresh_materialized_view(self):
        self._refresh_materialized_view()

    @api.multi
    def button_open_view(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.model_id.model,
            'view_id': self.view_id.id,
            'view_type': 'graph',
            'view_mode': 'graph',
        }

    # Prepare Function
    @api.multi
    def _prepare_model(self):
        self.ensure_one()
        return {
            'name': self.name,
            'model': self.technical_name,
        }

    @api.multi
    def _prepare_cron(self):
        self.ensure_one()
        return {
            'name': _('Refresh Materialized View %s') % (self.technical_name),
            'user_id': SUPERUSER_ID,
            'model': 'bi.sql.view',
            'function': 'button_refresh_materialized_view',
            'args': repr(([self.id],))
        }

    @api.multi
    def _prepare_view(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'graph',
            'model': self.model_id.model,
            'arch':
                """<?xml version="1.0"?>"""
                """<graph string="Analysis" type="pivot" stacked="True">{}"""
                """</graph>""".format("".join(
                    [x._prepare_field() for x in self.bi_sql_field_ids]))
             }

    @api.multi
    def _prepare_action(self):
        self.ensure_one()
        return {
            'name': self.name,
            'res_model': self.model_id.model,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'graph',
            'view_id': self.view_id.id,
        }

    @api.multi
    def _prepare_menu(self):
        self.ensure_one()
        return {
            'name': self.name,
            'parent_id': self.env.ref('bi_sql_editor.menu_bi_sql_editor').id,
            'action': 'ir.actions.act_window,%s' % (self.action_id.id),
        }

    # Custom Section
    def _log_execute(self, req):
        _logger.info("Executing SQL Request %s ..." % (req))
        self._cr.execute(req)

    @api.multi
    def _drop_view(self):
        for sql_view in self:
            self._log_execute(
                "DROP %s VIEW IF EXISTS %s" % (
                    sql_view.materialized_text, sql_view.technical_name))
            sql_view.size = False

    @api.multi
    def _create_view(self):
        self._drop_view()
        for sql_view in self:
            sql_view._drop_view()
            try:
                self._log_execute(
                    "CREATE %s VIEW %s AS (%s);" % (
                        self.materialized_text, sql_view.technical_name,
                        sql_view.sql_request))
                sql_view._refresh_size()
            except ProgrammingError as e:
                raise Warning(_(
                    "SQL Error while creating %s VIEW %s :\n %s") % (
                        sql_view.materialized_text, sql_view.technical_name,
                        e.message))

    @api.multi
    def _create_index(self):
        for sql_view in self:
            for sql_field in sql_view.bi_sql_field_ids.filtered(
                    lambda x: x.is_index is True):
                self._cr.execute(
                    "CREATE INDEX %s ON %s (%s);" % (
                        sql_field.index_name, sql_view.technical_name,
                        sql_field.name))
            sql_view._refresh_size()

    @api.multi
    def _drop_index(self):
        for sql_view in self:
            for sql_field in sql_view.bi_sql_field_ids.filtered(
                    lambda x: x.is_index is True):
                self._cr.execute("DROP INDEX %s" % (sql_field.index_name))
            sql_view._refresh_size()

    @api.multi
    def _create_model(self):
        for sql_view in self:
            vals = self._prepare_model()
            # Prevent table creation
            vals['state'] = 'base'
            model = self.env['ir.model'].create(vals)
            # Set model as a 'Custom Object'
            model.write({'state': 'manual'})
            sql_view.model_id = model.id

    @api.multi
    def _refresh_schema(self):
        sql_field_obj = self.env['bi.sql.field']
        for sql_view in self:
            sql_view.bi_sql_field_ids.unlink()
            req = """
                SELECT  attnum,
                        attname AS column,
                        format_type(atttypid, atttypmod) AS type
                FROM    pg_attribute
                WHERE   attrelid = '%s'::regclass
                AND     NOT attisdropped
                AND     attnum > 0
                ORDER   BY attnum;"""
            self._cr.execute(req % (sql_view.technical_name))
            res = self._cr.fetchall()
            for column in res:
                res = sql_field_obj.create({
                    'sequence': column[0],
                    'name': column[1],
                    'sql_type': column[2],
                    'bi_sql_view_id': sql_view.id,
                })

    @api.multi
    def _refresh_materialized_view(self):
        for sql_view in self:
            self._log_execute(
                "REFRESH %s VIEW %s" % (
                    self.materialized_text, sql_view.technical_name))
            sql_view._refresh_size()

    @api.multi
    def _refresh_size(self):
        for sql_view in self:
            self._cr.execute(
                "SELECT pg_size_pretty(pg_total_relation_size('%s'));" % (
                    sql_view.technical_name))
            sql_view.size = self._cr.fetchone()[0]
