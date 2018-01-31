winthrop-django
===============

.. sphinx-start-marker-do-not-remove

Django web application for `The Winthrop Family on the
Page <https://digitalhumanities.princeton.edu/projects/TheWinthropFamilyonthePage/>`__
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


Development instructions
------------------------

Initial setup and installation:

-  recommended: create and activate a python 3.5 virtualenv::
   virtualenv winthrop -p python3.5
   source winthrop/bin/activate

-  pip install required python dependencies::
   pip install -r requirements.txt
   pip install -r dev-requirements.txt

-  copy sample local settings and configure for your environment::
   cp winthrop/local_settings.py.sample winthrop/local_settings.py


Unit Tests
~~~~~~~~~~

Unit tests are written with `py.test <http://doc.pytest.org/>`__ but use
Django fixture loading and convenience testing methods when that makes
things easier. To run them, first install development requirements::

    pip install -r dev-requirements.txt

Run tests using py.test::

    py.test

Documentation
~~~~~~~~~~~~~

Documentation is generated using `sphinx <http://www.sphinx-doc.org/>`__
To generate documentation them, first install development requirements::

    pip install -r dev-requirements.txt

Then build documentation using the customized make file in the `sphinx-docs`
directory::

    cd sphinx-docs
    make docs

The documentation will be available in the directory `docs`.    

You can also view documentation for the current master branch `on GitHub Pages <https://princeton-cdh.github.io/winthrop-django/>`__
