.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================================
BI Views builder, based on Materialized or Normal SQL Views
===========================================================

This module extends the functionality of reporting, to support creation
of extra custom reports.
It allows admin user to write a custom SQL request.
Once written, a new model is generated, and admin can map the selected field
with odoo fields.
Then admin ends the process, creating new menu, action and graph view.

Technically, the module create SQL View (or materialized view, if option is
checked). Materialized view duplicate datas, but request are fastest. If
materialized view is enabled, this module will create a cron task, 

Warning
-------
This module is intended for technician people in a company and for Odoo integrators.

It requires the user to know SQL syntax and Odoo models.

If you don't have such skills, do not try to use this module specially on a production
environment.

Use Cases
---------

this module is interesting for the following use cases

* You want to realize technical SQL requests, that Odoo framework doesn't allow
  (For exemple, UNION with many SELECT) A typical use case is if you want to have
  sale and PoS order datas in a same table

* You want to customize an Odoo report, removing some useless fields and adding
  some custom ones. In that case, you can simply select the fields of the original
  report (sale.report model for exemple), and add your custom fields

* You have a lot of data, and classical SQL Views have very bad performance.
  In that case, MATERIALIZED VIEW will be a good solution to reduce display duration

Configuration
=============

To configure this module, you need to:

* Go to Settings / Technical / Database Structure / SQL Views

* tip your SQL request

  .. figure:: /bi_sql_editor/static/description/01_sql_request.png
     :width: 600 px

* Once the view created, the module analyse the column of the view,
  and propose field mapping. For each field, you can decide to create an index
  and set if it will be displayed on the pivot graph as a column, a row or a
  measure. If it's a MATERIALIZED view, a cron task is created to refresh
  the view. You can so define the frequency of the refresh.

  .. figure:: /bi_sql_editor/static/description/02_field_mapping.png
     :width: 600 px

* Once the mapping realized, and the indexes created, the wizard will
  create menu item, action and graph views.

  .. figure:: /bi_sql_editor/static/description/03_final_setting.png
     :width: 600 px

Usage
=====

To use this module, you need to:

* Go to 'Reporting' / 'Custom Reports' 

* select the desired report

  .. figure:: /bi_sql_editor/static/description/04_reporting.png
     :width: 600 px

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/8.0


WIP - features to implement
===========================

* Demo : Add demo data.
* Security : Groups to the module models.
* Possibility to add groups to created models. (avoiding warning) (ir.model.access)
* Possibility to add rules to the created models (ir.rule)
* refactor creation. (create model and field in the same step + refresh )
* refactor wizard. -> To allow user to mass create fields
* [FIX] model guess do not work
* Add 'interval', after type (row/col/measure) field for date(time) fields.
* on row/col field, automatically create a search view with according fields.

Known issues / Roadmap
======================

* simplify SQL requests
    * allow field without prefix x_
    * allow ';' at the end

* prevent maliscious SQL requests

* Dinamically change displayed action name to mention the last refresh of the
  materialized view. (require extra community module.) (server-tools ?)

* When setting to draft, it could great to keep the model, to avoid to map again
  interesting, if we add / remove one new column  in the SQL View

  Better Idea ! Remove the wizard : keep the two value for function.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

* This module is highly inspired by the work of

#. Onestein: (http://www.onestein.nl/)
   Module: OCA/server-tools/bi_view_editor.
   Link: https://github.com/OCA/reporting-engine/tree/8.0/bi_view_editor
#. Anybox: (https://anybox.fr/)
   Module : OCA/server-tools/materialized_sql_view
   link: https://github.com/OCA/server-tools/pull/110
#. GRAP, Groupement Régional Alimentaire de Proximité: (http://www.grap.coop/)
   Module: grap/odoo-addons-misc/pos_sale_reporting
   link: https://github.com/grap/odoo-addons-misc/tree/7.0/pos_sale_reporting


Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
