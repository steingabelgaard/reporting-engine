# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BI SQL Editor',
    'summary': "BI Views builder, based on Materialized / Classic Views",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Reporting',
    'author': 'GRAP,Odoo Community Association (OCA)',
    'website': 'https://www.odoo-community.org',
    'depends': [
        'web',
    ],
    'data': [
        'views/action_button.xml',
        'views/view_bi_sql_view.xml',
        'views/view_bi_sql_field_wizard.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/res_groups.xml',
    ],
    'images': [],
    'installable': True,
}
