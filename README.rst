winthrop-django
===============

.. sphinx-start-marker-do-not-remove

Django web application for `The Winthrop Family on the
Page <https://cdh.princeton.edu/projects/the-winthrop-family-on-the-page/>`__
project.

Python 3.5 / Django 1.10

.. image:: https://travis-ci.org/Princeton-CDH/winthrop-django.svg?branch=master
    :target: https://travis-ci.org/Princeton-CDH/winthrop-django
    :alt: Build status

.. image:: https://codecov.io/gh/Princeton-CDH/winthrop-django/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Princeton-CDH/winthrop-django/branch/master
    :alt: Code coverage

.. image:: https://landscape.io/github/Princeton-CDH/winthrop-django/master/landscape.svg?style=flat
    :target: https://landscape.io/github/Princeton-CDH/winthrop-django/master
    :alt: Code Health

.. image:: https://landscape.io/github/Princeton-CDH/winthrop-django/master/landscape.svg?style=flat
    :target: https://requires.io/github/Princeton-CDH/winthrop-django/requirements/?branch=master
    :alt: Requirements Status

This repo uses `git-flow <https://github.com/nvie/gitflow>`_ conventions; **master**
contains the most recent release, and work in progress will be on the **develop** branch.
Pull requests should be made against develop.

Development instructions
------------------------

Initial setup and installation:

- **recommended:** create and activate a python 3.5 virtualenv::

     virtualenv ppa -p python3.5
     source ppa/bin/activate

- Use pip to install required python dependencies::

    pip install -r requirements.txt
    pip install -r dev-requirements.txt

- Copy sample local settings and configure for your environment::

   cp ppa/local_settings.py.sample ppa/local_settings.py

- Create a database, configure in local settings, and run migrations::

    python manage.py migrate

- Create two new Solr cores with a basic configuration and managed schema,
  using the core/collection names for development and testing that you
  configured in local settings::

    solr create -c SOLR_CORE -n basic_configs
    solr create -c SOLR_TEST_CORE -n basic_configs

- Run the manage command to configure the schema::

    python manage.py solr_schema

  The manage command will automatically reload the core to ensure schema
  changes take effect.

- Then index data into Solr::

    python manage.py index


Tests
~~~~~~~~~~

Python unit tests are written with `py.test <http://doc.pytest.org/>`_ but use
Django fixture loading and convenience testing methods when that makes
things easier. To run them, first install development requirements::

    pip install -r dev-requirements.txt

Run tests using py.test.  Note that this currently requires the
top level project directory be included in your python path.  You can
accomplish this either by calling pytest via python::

    python -m pytest

Or, if you wish to use the ``pytest`` command directly, simply add the
top-level project directory to your python path environment variable::

  setenv PYTHONPATH .  # csh
  export PYTHONPATH=.  # bash

Make sure you configure a test solr connection and set up an empty
Solr core using the same instructions as for the development core.


Documentation
-------------

You can view documentation for the current master branch `on GitHub Pages. <https://princeton-cdh.github.io/winthrop-django/>`__

Documentation is generated using `sphinx. <http://www.sphinx-doc.org/>`__
To generate documentation, first install development requirements::

    pip install -r dev-requirements.txt

Then build documentation using the customized make file in the ``docs``
directory::

    cd sphinx-docs
    make html

When building for a release ``make docs`` will create a folder called ``docs``,
build the HTML documents and static assets, and force add it to the commit for
use with Github Pages.


License
-------
This project is licensed under the `Apache 2.0 License <https://github.com/Princeton-CDH/ppa-django/blob/master/LICENSE>`_.
