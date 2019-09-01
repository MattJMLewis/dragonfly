Installation
===============

Installing Python
^^^^^^^^^^^^^^^^^

For dragonfly to work you must have Python 3.6 or above installed. For
further details on how to do this please see
`here <https://www.python.org/downloads/>`__.

Installing Dragonfly
^^^^^^^^^^^^^^^^^^^^

First, download the Dragonfly repository

- Via git

    ``git clone git@github.com:MattJMLewis/dragonfly.git``

- Via GitHub

    Simply download the
    `repository <https://github.com/MattJMLewis/dragonfly/archive/master.zip>`__
    and unzip it.

Installing requirements
^^^^^^^^^^^^^^^^^^^^^^^

Next, enter the dragonfly directory and run the following command.

``pip install -r requirements.txt``

On Windows you may encounter an error installing ``mysqlclient``. If this happens you can download the latest ``.whl``
`here <https://pypi.org/project/mysqlclient/#files>`__. There is also an unoffical repo of ``.whl`` files `here <https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient>`__. Then simply run ``pip install name-of-the-whl-file.whl``.

Setting up a MySQL database
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dragonfly currently only supports ``MySQL`` databases. See
`here <https://dev.mysql.com/doc/refman/8.0/en/installing.html>`__ for
more details on how to set up a server.

Running dragonfly
^^^^^^^^^^^^^^^^^

- Development

    Simply run the ``main.py`` file. However before you do this you should
    modify the ``config.py`` file to match your setup.

- Production

    Coming soon...

Usage
^^^^^

Please see :doc:`here <quick-start>` for the quick start guide on using
dragonfly.
