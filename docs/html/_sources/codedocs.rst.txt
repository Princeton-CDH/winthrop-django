Code Documentation
==================

.. toctree::
   :maxdepth: 2

Common
------
.. automodule:: winthrop.common
    :members:

Models
^^^^^^
.. automodule:: winthrop.common.models
    :members:

Places
-------
.. automodule:: winthrop.places
    :members:

Models
^^^^^^
.. automodule:: winthrop.places.models
    :members:

Views
^^^^^
.. automodule:: winthrop.places.views
    :members:

GeoNames
^^^^^^^^
.. automodule:: winthrop.places.geonames
    :members:

Books
-----
.. automodule:: winthrop.books
    :members:

Models
^^^^^^
.. automodule:: winthrop.books.models
    :members:

Views
^^^^^
.. automodule:: winthrop.books.views
    :members:

import_nysl
^^^^^^^^^^^
.. automodule:: winthrop.books.management.commands.import_nysl

  Import command for Winthrop team's spreadsheet. It can be invoked using::

    python manage.py import_nysql [--justsammel] /path/to/csv

  The ``--justsammel`` flag skips import of records to avoid
  reproducing duplicates, but rebuilds the ```is_sammelband`` flag set and
  produces an output list.

  The expect behavior is designed for a once-off import and will produce
  duplicate book entries (but not duplicates of any entries created
  as part of book creation).

  All persons created attempt to have a VIAF uri associated and all places
  have a Geonames ID assigned if possible.

People
------
.. automodule:: winthrop.people
    :members:

Models
^^^^^^
.. automodule:: winthrop.people.models
    :members:

Views
^^^^^
.. automodule:: winthrop.people.views
    :members:

VIAF
^^^^^
.. automodule:: winthrop.people.viaf
    :members:

Footnotes
---------
.. automodule:: winthrop.footnotes
    :members:

Models
^^^^^^
.. automodule:: winthrop.footnotes.models
    :members:
