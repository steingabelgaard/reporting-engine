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


class BiSQLViewField(models.Model):
    _name = 'bi.sql.view.field'
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

    field_description = fields.Char(
        string='Field Description', help="This will be used as the name"
        " of the Odoo field, displayed for users")

    ttype = fields.Selection(
        string='Field Type', selection=_TTYPE_SELECTION, help="type of the"
        " odoo field that will be created")

    selection = fields.Char(
        string='Selection Options', default='[]',
        help="List of options for a selection"
        " field, specified as a Python expression defining a list of"
        " (key, label) pairs. For example:"
        " [('blue','Blue'),('yellow','Yellow')]")

    many2one_model_id = fields.Many2one(
        comodel_name='ir.model', string='Model',
        help="Model for a Many2one field")

    # Compute Section
    @api.multi
    def _compute_index_name(self):
        for sql_field in self:
            sql_field.index_name = '%s_%s' % (
                sql_field.bi_sql_view_id.view_name, sql_field.name)

    # Overload Section
    @api.multi
    def unlink(self):
        self.mapped('field_id').unlink()
        return super(BiSQLViewField, self).unlink()

    # Custom Section
    @api.multi
    def _prepare_field(self):
        self.ensure_one()
        res = ''
        if self.graph_type and self.field_id:
            res = """<field name="{}" type="{}" />""".format(
                self.field_id.name, self.graph_type)
        return res
