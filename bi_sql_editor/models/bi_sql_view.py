# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from psycopg2 import ProgrammingError

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.exceptions import Warning
from openerp.modules.registry import RegistryManager

#_STATE_SELECTION = [
#    ('draft', 'Draft'),
#    ('sql_view_created', 'SQL View Created'),
#    ('registry_updated', 'Registry Updated'),
#    ('ui_created', 'UI Created'),
#]

_logger = logging.getLogger(__name__)


class BiSQLView(models.Model):
    _name = 'bi.sql.view'
    _inherit = ['sql.request.mixin']

    _sql_prefix = 'x_bi_sql_view_'

    _model_prefix = 'x_bi_sql_view.'

    _sql_request_groups_relation = 'bi_sql_view_groups_rel'

    _sql_request_users_relation = 'bi_sql_view_users_rel'

    technical_name = fields.Char(
        string='Technical Name', required=True,
        help="Suffix of the SQL view. (SQL full name will be computed and"
        " prefixed by 'x_bi_sql_view_'. Should have correct"
        "syntax. For more information, see https://www.postgresql.org/"
        "docs/current/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS")

    view_name = fields.Char(
        string='View Name', compute='_compute_view_name', readonly=True,
        store=True, help="Full name of the SQL view")

    model_name = fields.Char(
        string='Model Name', compute='_compute_model_name', readonly=True,
        store=True, help="Full Qualified Name of the transient model that will"
        " be created.")

    is_materialized = fields.Boolean(
        string='Is Materialized View', default=True, readonly=True,
        states={'draft': [('readonly', False)]})

    materialized_text = fields.Char(
        compute='_compute_materialized_text', store=True)

    size = fields.Char(
        string='Database Size', readonly=True,
        help="Size of the materialized view and its indexes")

#    state = fields.Selection(
#        string='State', required=True, selection=_STATE_SELECTION,
#        default='draft')

    bi_sql_view_field_ids = fields.One2many(
        string='SQL Fields', comodel_name='bi.sql.view.field',
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
    @api.depends('is_materialized')
    @api.multi
    def _compute_materialized_text(self):
        for sql_view in self:
            sql_view.materialized_text =\
                self.is_materialized and 'MATERIALIZED' or ''

    @api.depends('technical_name')
    @api.multi
    def _compute_view_name(self):
        for sql_view in self:
            sql_view.view_name = '%s%s' % (
                self._sql_prefix, self.technical_name)

    @api.depends('technical_name')
    @api.multi
    def _compute_model_name(self):
        for sql_view in self:
            sql_view.model_name = '%s%s' % (
                self._model_prefix, self.technical_name)

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
##    @api.multi
##    def button_set_draft(self):
##        self._drop_index()
##        self._drop_view()
##        self.bi_sql_view_field_ids.unlink()
##        self.model_id.unlink()
##        self.view_id.unlink()
##        self.action_id.unlink()
##        self.menu_id.unlink()
##        self.cron_id.unlink()
##        self.write({'state': 'draft'})

##    @api.multi
##    def button_create_sql_view(self):
##        if any([x.state != 'draft' for x in self]):
##            raise _("You can only process this action on draft items")
##        self._create_view()
##        self._create_model()
##        self._refresh_schema()
##        if self.is_materialized:
##            self.cron_id = self.env['ir.cron'].create(
##                self._prepare_cron()).id
##        self.write({'state': 'sql_view_created'})

##    @api.multi
##    def button_update_registry(self):
##        RegistryManager.new(self.env.cr.dbname, update_module=True)
##        RegistryManager.signal_registry_change(self.env.cr.dbname)
##        self._create_index()
##        self.write({'state': 'registry_updated'})

##    @api.multi
##    def button_create_ui(self):
##        self.view_id = self.env['ir.ui.view'].create(
##            self._prepare_view()).id
##        self.action_id = self.env['ir.actions.act_window'].create(
##            self._prepare_action()).id
##        self.menu_id = self.env['ir.ui.menu'].create(
##            self._prepare_menu()).id
##        self.write({'state': 'ui_created'})

##    @api.multi
##    def button_refresh_materialized_view(self):
##        self._refresh_materialized_view()

##    @api.multi
##    def button_open_view(self):
##        return {
##            'type': 'ir.actions.act_window',
##            'res_model': self.model_id.model,
##            'view_id': self.view_id.id,
##            'view_type': 'graph',
##            'view_mode': 'graph',
##        }

    # Prepare Function
    @api.multi
    def _prepare_model(self):
        self.ensure_one()
        return {
            'name': self.name,
            'model': self.model_name,
        }

    @api.multi
    def _prepare_cron(self):
        self.ensure_one()
        return {
            'name': _('Refresh Materialized View %s') % (self.view_name),
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
                    [x._prepare_field() for x in self.bi_sql_view_field_ids]))
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
        self.env.cr.execute(req)

    @api.multi
    def _drop_view(self):
        for sql_view in self:
            self._log_execute(
                "DROP %s VIEW IF EXISTS %s" % (
                    sql_view.materialized_text, sql_view.view_name))
            sql_view.size = False

    @api.multi
    def _create_view(self):
        self._drop_view()
        for sql_view in self:
            sql_view._drop_view()
            try:
                self._log_execute(
                    "CREATE %s VIEW %s AS (%s);" % (
                        self.materialized_text, sql_view.view_name,
                        sql_view.query))
                sql_view._refresh_size()
            except ProgrammingError as e:
                raise Warning(_(
                    "SQL Error while creating %s VIEW %s :\n %s") % (
                        sql_view.materialized_text, sql_view.view_name,
                        e.message))

    @api.multi
    def _create_index(self):
        for sql_view in self:
            for sql_field in sql_view.bi_sql_view_field_ids.filtered(
                    lambda x: x.is_index is True):
                self.env.cr.execute(
                    "CREATE INDEX %s ON %s (%s);" % (
                        sql_field.index_name, sql_view.view_name,
                        sql_field.name))
            sql_view._refresh_size()

    @api.multi
    def _drop_index(self):
        for sql_view in self:
            for sql_field in sql_view.bi_sql_view_field_ids.filtered(
                    lambda x: x.is_index is True):
                self.env.cr.execute("DROP INDEX %s" % (sql_field.index_name))
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
    def _hook_executed_request(self):
        self.ensure_one()
        req = """
            SELECT  attnum,
                    attname AS column,
                    format_type(atttypid, atttypmod) AS type
            FROM    pg_attribute
            WHERE   attrelid = '%s'::regclass
            AND     NOT attisdropped
            AND     attnum > 0
            ORDER   BY attnum;"""
        self.env.cr.execute(req % (self.view_name))
        res = self.env.cr.fetchall()
        return res

    @api.multi
    def _prepare_request_check_execution(self):
        self.ensure_one()
        return "CREATE VIEW %s AS (%s);" % (self.view_name, self.query)

    @api.multi
    def _check_execution(self):
        """Ensure that the query is valid, trying to execute it.
        a non materialized view is created for this check.
        A rollback is done at the end.
        After the execution, and before the rollback, an analysis of
        the database structure is done"""
        self.ensure_one()
        sql_view_field_obj = self.env['bi.sql.view.field']
        columns = super(BiSQLView, self)._check_execution()
        print columns
        field_ids = []
        for column in columns:
            existing_field = self.bi_sql_view_field_ids.filtered(
                lambda x: x.name == column[1])
            if existing_field:
                # Update existing field
                field_ids.append(existing_field.id)
                existing_field.write({
                    'sequence': column[0],
                    'sql_type': column[2],
                })
            else:
                # Create a new one
                field_ids.append(sql_view_field_obj.create({
                    'sequence': column[0],
                    'name': column[1],
                    'sql_type': column[2],
                    'bi_sql_view_id': self.id,
                }).id)
        # Drop obsolete view field
        self.bi_sql_view_field_ids.filtered(
            lambda x: x.id not in field_ids).unlink()

        return columns

    @api.multi
    def _refresh_materialized_view(self):
        for sql_view in self:
            self._log_execute(
                "REFRESH %s VIEW %s" % (
                    self.materialized_text, sql_view.view_name))
            sql_view._refresh_size()

    @api.multi
    def _refresh_size(self):
        for sql_view in self:
            self.env.cr.execute(
                "SELECT pg_size_pretty(pg_total_relation_size('%s'));" % (
                    sql_view.view_name))
            sql_view.size = self.env.cr.fetchone()[0]
