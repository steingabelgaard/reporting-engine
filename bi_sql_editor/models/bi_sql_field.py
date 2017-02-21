# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models

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


class BiSQLField(models.Model):
    _name = 'bi.sql.field'
    _order = 'sequence'

    _GRAPH_TYPE_SELECTION = [
        ('col', 'Column'),
        ('row', 'Row'),
        ('measure', 'Measure'),
    ]

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

    field_id = fields.Many2one(
        string='Field', comodel_name='ir.model.fields')

    # Compute Section
    @api.multi
    def _compute_index_name(self):
        for sql_field in self:
            sql_field.index_name = '%s_%s' % (
                sql_field.bi_sql_view_id.technical_name, sql_field.name)

    # Overload Section
    @api.multi
    def unlink(self):
        self.mapped('field_id').unlink()
        return super(BiSQLField, self).unlink()

    # Custom Section
    @api.multi
    def _prepare_field(self):
        self.ensure_one()
        res = ''
        if self.graph_type and self.field_id:
            res = """<field name="{}" type="{}" />""".format(
                self.field_id.name, self.graph_type)
        return res
