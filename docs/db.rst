Database
====================

DB
^^
.. automodule:: dragonfly.db.database
   :members:
   :undoc-members:
   :show-inheritance:

Fields
^^^^^^
.. note::
    - Please note that the majority of MySQL field types are available for usage. There name will just be the camel case of the MySQL type with ``Field`` appended.
    - All fields accept the following parameters: ``null``, ``default``, ``unique``, ``primary_key``. These values are, by default, ``False``. Some fields will have extra parameters which can be seen below.


.. automodule:: dragonfly.db.models.fields
   :members:
   :undoc-members:
   :show-inheritance:

Model
^^^^^
.. automodule:: dragonfly.db.models.model
   :members:
   :undoc-members:
   :show-inheritance:

Relationships
^^^^^^^^^^^^^
.. automodule:: dragonfly.db.models.relationships
   :members:
   :undoc-members:
   :show-inheritance:

.. warning:: The following classes should not be called directly.

DatabaseMigrator
^^^^^^^^^^^^^^^^
.. automodule:: dragonfly.db.database_migrator
   :members:
   :undoc-members:
   :show-inheritance:

Table
^^^^^
.. automodule:: dragonfly.db.table
   :members:
   :undoc-members:
   :show-inheritance:

