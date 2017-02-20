.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================================================
BI Views builder, based on Materialized / Classic Views
=======================================================

This module extends the functionality of reporting, to support creation
of extra custom report.
It allows admin user to write a custom SQL request.
Once written, a new model is generated, and admin can map the selected field
with odoo fields.
Then admin ends the process, creating new menu, action and graph view.

Technically, the module create SQL View (or materialized view, if option is
checked). Materialized view duplicate datas, but request are fastest. If
materialized view is enabled, this module will create a cron task, 

Warning
-------
This module intended for technician people in a company and for Odoo integrators.

It requires that the user knows SQL syntax and Odoo models.

If you don't have such skills, do not try to use this module in a production
database.

Configuration
=============

To configure this module, you need to:

#. Go to Settings / Technical / Database Structure / SQL Views
#. TODO

.. figure:: path/to/local/todo.png
   :width: 600 px

Usage
=====

To use this module, you need to:

#. Go to 'Reporting' / 'Custom Reports' and select the desired report
#. 

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/8.0


Known issues / Roadmap
======================

* Add Groups to model. (avoiding warning)
* when creating fields, set it to manual, instead base
* once fields created, reload registry
* create Cron Task
* Create 

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

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)
* Company 2 name

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

