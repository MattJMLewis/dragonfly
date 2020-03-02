Quick Start
===========
.. _quick-start:

This guide assumes you already have Dragonfly installed. Please see the
:doc:`installation <installation>` section if you do not.


Design Philosophy
^^^^^^^^^^^^^^^^^
Dragonfly is based on the
`model-view-controller <https://en.wikipedia.org/wiki/Model-view-controller>`__ architectural pattern. This means that the model structure, application
logic and user interface are divided into separate components. As this is a brief quick start guide some features
won't be shown. To get a full list of features please see the :doc:`API reference <api-reference>`.

This quick guide details some of the code in the demo project that is displayed on this site.

Routing
^^^^^^^

Routing allows Dragonfly to know the location to send a HTTP request. In
the example below the GET request to ``/users/<id:int>`` is routed to the
``show`` function on ``UserController``. This is all registered in the
``routes.py`` file.

.. code:: python

    from dragonfly.routes import routes

    routes.get('users/<id:int>', 'UserController@show')

HTTP Methods
''''''''''''

Dragonfly supports the following HTTP methods:

+--------------------+------------------+
| HTTP Method        | Router method    |
+====================+==================+
| GET                | ``.get()``       |
+--------------------+------------------+
| POST               | ``.post()``      |
+--------------------+------------------+
| PUT                | ``.put()``       |
+--------------------+------------------+
| PATCH              | ``.patch()``     |
+--------------------+------------------+
| OPTIONS            | ``.options()``   |
+--------------------+------------------+
| DELETE             | ``.delete()``    |
+--------------------+------------------+
| All of the above   | ``.any()``       |
+--------------------+------------------+

Resource Routing
''''''''''''''''

The ``Router`` class also has a special method called ``resource``. Its
second argument is an entire controller. Here is an example:

.. code:: python

    routes.resource('articles', 'ArticleController') # Notice there is no @{method_name}

Calling ``.resource('ArticleController')`` will register the following routes:

+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| Route                         | HTTP Method   | Controller function            | Description                                                  |
+===============================+===============+================================+==============================================================+
| ``/articles``                 | GET           | ``ArticleController@index``    | Return all articles in the database.                         |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| ``/articles/<id:int>``        | GET           | ``ArticleController@show``     | Return the article with the given id or fail.                |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| ``/articles/create``          | GET           | ``ArticleController@create``   | Show the form to create a new article.                       |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| ``/articles``                 | POST          | ``ArticleController@stores``   | Store (and validate) the given values in the POST request.   |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| ``/articles/<id:int>/edit``   | GET           | ``ArticleController@edit``     | Show the form to edit a article.                             |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| ``/articles/<id:int>``        | PUT           | ``ArticleController@update``   | Update the given article using the given values.             |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+
| ``/articles/<id:int>``        | DELETE        | ``ArticleController@delete``   | Delete the given article.                                    |
+-------------------------------+---------------+--------------------------------+--------------------------------------------------------------+

Route Parameters
''''''''''''''''

Route parameters are a way of passing variables to the controller to
help find a certain piece of data. In the example above if the
URL\  ``/articles/1`` was called, the integer ``1`` would be passed to
the controller ``show`` function through a variable named ``id``. This
allows for the look up and return of the given article from the
database. A route parameter should follow the pattern below:

.. code:: python

    <name_of_variable:expected_type>

It is possible to have multiple parameters on a route. For example:

.. code:: python

    routes.get('/articles/<id:int>/<comment_id:int>')

Dragonfly supports the following types by default:

+-----------+----------------+
| Type      | Regex          |
+===========+================+
| ``int``   | ``([0-9]+)``   |
+-----------+----------------+
| ``str``   | ``(.+)``       |
+-----------+----------------+

Custom types
************
It is very easy to define your own custom types. Simply add a new key
(name of the type), value (regex to match) pair in the
``PYTHON_TO_REGEX``\ dictionary in ``config.py``. For example:

.. code:: python

    PYTHON_TO_REGEX = {"int": "([0-9]+)", "str": "(.+)", 
                       "str_capitalised": "(\b[A-Z].*?\b)"}

Controllers
^^^^^^^^^^^
A controller should contain all of your application logic to do with
that resource. The following command will create a file in the
``controllers`` directory called ``article_controller``:

::

    python builder.py generate --type=controller article_controller

Each time a request is routed a new instance of the registered
controller will be instantiated and the registered function run.

The following is the basic structure of a controller:

.. code:: python

    from dragonfly import Auth, view
    from models.article import Article

    class ArticleController:
        
        def show(self, id):
            return View('articles.show', article=Article().find(id), user=Auth.user())
            

The following route would match to this controller method:

.. code:: python

    routes.get('/articles/<id:int>', 'ArticleController@show')

A controller method should always return a ``Response`` class of some sort.

Middleware
^^^^^^^^^^
Middleware provides a way to stop or modify a request cycle. This can occur before the
request is routed, after a response is returned from the controller or
both. Dragonfly comes with a few premade middleware such as CSRF protection and a user middleware. You can also create
your own middleware using the following command:

.. code:: python

    python builder.py generate --type=middleware article_middleware

The following is an example of middleware that will run on any route
that resolves the ``show`` method in the ``ArticleController``. It is
possible to assign a middleware to multiple actions by appending to the
``actions`` list. The ``before`` method here uses the singleton of the
``DeferredResponse`` class to set the header for the response before it
has been generated (NOTE: This does **not** set the headers for any
``Response`` other than the one returned by the controller).

In the ``before`` and ``after`` method if any ``Response`` class or
child of the ``Response`` class is returned the processing of the
request will stop and the response returned.

.. code:: python

    from dragonfly import request
    from dragonfly import ErrorResponse, deferred_response

    class ArticleMiddleware:

        actions = ['ArticleController@show']

        def before(self):
            if visited in request.cookies:
                return ErrorResponse(404, "You have already visited the page.")
                
            deferred_response.header('Set-Cookie', 'visited=True')
            

        def after(self):
            pass

Below is an example of the CSRF protection middleware class that comes pre-packaged with Dragonfly.

.. warning:: Please note that in any ``Middleware`` class object any packages imported from the framework must be imported by their full import path. This is as the actual middleware file is executed in the package middleware directory.

.. code:: python

    from dragonfly.constants import DATA_METHODS
    from dragonfly.request import request
    from dragonfly.response import ErrorResponse
    from dragonfly.auth import Auth
    from config import NO_AUTH

    import os


    class CsrfMiddleware:
        actions = '*'

        def before(self):
            # Determine if csrf_token for form request is valid
            if request.method in DATA_METHODS and request.path not in NO_AUTH:

                try:
                    token = request.get_data()['csrf_token']
                except KeyError:
                    return ErrorResponse('No CSRF token', 500)

                if token != Auth.get('csrf_token'):
                    return ErrorResponse('CSRF invalid', 500)

            # Set a csrf_token for the form request
            elif request.path not in NO_AUTH:
                Auth.set('csrf_token', os.urandom(25).hex())

        def after(self):
            pass

Database
^^^^^^^^
The database module provides any easy way to interact with the configured
``MySQL`` database. It simply provides Python functions that are equivalent
to most commonly used SQL commands.

The code below demonstrates some of its usage (note this code is not present in the actual demo application)

.. code:: python

    res = DB('articles').select('name').where('name', '=', 'Testing').first()

This will generate and execute the following SQL code:

.. code:: sql

    SELECT 'name' FROM `articles` WHERE 'name' = 'testing';


Models (ORM)
^^^^^^^^^^^^
Models provide an easy way to read, write and update a table in the
database through a Python class. To start using the ORM you first need
to define the attributes of a model. This is all done through a model
class file. This can be generated using the CLI:

::

    python builder.py generate --type=model article

A new file will be created in the ``models`` directory. Below is an
example of an articles model and the SQL it generates.

.. code:: python

    from dragonfly import models

    class Article(models.Model):

        name = models.VarCharField(length=255)
        text = models.TextField()
        user_id = models.IntField(unsigned=True)

        class Meta:
            article_user_fk = models.ForeignKey('user_id').references('id').on('users')

        def url(self):
        return f"{URL}/articles/{self.id}"


There are many field types and options for each field type. For an
exhaustive list of these please see the :doc:`API
reference <api-reference>`. It is also important to note that you
can add any function you would like to the model class. For example a
way to generate the slug for an article:

.. code:: python

        def url(self):
            return f"/articles/{self.id}"

This is also where relationships are defined. The following code would be used to define a one-to-many relationship
with the ``Comments`` class and a many-to-one relationship with the ``User`` class.

.. code:: python

        def comments(self):
            return self.add_relationship(models.HasMany(target='comment'))

        def user(self):
            return self.add_relationship(models.BelongsTo(target='user'))


Once you have defined the model you need to generate and execute the SQL
to create the needed tables. To do this simply run the following command.

::

    python builder.py migrate

Once complete you should be able to manipulate the newly created
``articles`` table through the ``Article`` model. Below is an example of
retrieving all articles in the database:

::

    from models.article import Article

    articles = Article().get()

The ORM has a large number of methods that are all listed in the :doc:`API reference <api-reference>`.

To interact with the relationships defined in the class simply call the defined functions.

.. code:: python

    # Returns a list of ``Comment`` objects that belong to the given ``Article`` class
    comments = Article().first().comments()

    # Returns the ``User`` object that this ``Article`` belongs to.
    user = Article().first().user()

Templates
^^^^^^^^^
Dragonfly provides an easier way to join Python and HTML by using a templating system. A template is stored in the ``templates`` directory and should be a ``html``\ file. The
templates can also be in subdirectories of the ``templates`` directory.

Below is an example of a html file saved in
``templates/articles/index.html``

.. code:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Articles</title>
        <link rel="stylesheet" href="https://bootswatch.com/4/materia/bootstrap.min.css">
    </head>
    <body>
    <div class="navbar navbar-expand-lg fixed-top navbar-dark bg-primary">
        <div class="container">
            <a href="{{ Utils.url('') }}" class="navbar-brand">Dragonfly</a>
            <div class="collapse navbar-collapse" id="navbarResponsive">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ Utils.url('articles') }}">Articles</a>
                    </li>
                </ul>
                <form class="form-inline my-2 my-lg-0" method="POST" action="{{ Utils.url('logout') }}">
                    <input type="hidden" name="csrf_token" value="{{ Auth.get('csrf_token') )}}">
                    <button class="btn btn-secondary my-2 my-sm-0" type="submit">Log out</button>
                </form>
            </div>
        </div>
    </div>
    <div class="container mt-5 pt-5">
        <div class="row">
            <div class="col-lg-12">
                <div class="card border-secondary mb-3">
                    <div class="card-header">Articles</div>
                    <div class="card-body">
                        <div class="list-group list-group-flush">
                            @if(articles is None)
                                No articles
                            @else
                                @for(article in articles)
                                <a href="{{ $article.url()$ }}"
                                   class="list-group-item list-group-item-action flex-column align-items-start">
                                    <div class="d-flex w-100 justify-content-between">
                                        <h5 class="mb-1">{{ $article.name$ }}</h5>
                                    </div>
                                    <p class="mb-1">{{ $article.text$ }}</p>
                                </a>
                                @endfor
                            @endif
                        </div>
                    </div>
                </div>
                <a href="{{ Utils.url('articles/create') }}"><button type="button" class="btn btn-primary btn-lg btn-block">Create an Article</button></a>

                @if(pagination is not None)
                    @if(pagination['last_page'] != 1)
                    <div class="btn-toolbar justify-content-center" role="toolbar">
                        <div class="btn-group mr-2" role="group" aria-label="First group">
                            @for(i in range(0, pagination['last_page']))
                            <a href="{{ Utils.url('articles?page=' + str(i + 1)) }}">
                                <button type="button" class="btn btn-secondary">{{ $(i + 1)$ }}</button>
                            </a>
                            @endfor
                        </div>
                    </div>
                    @endif
                @endif
            </div>
        </div>
    </div>
    </body>
    </html>

To call and render this view you would write the following in your
controller:

.. code:: python

    articles = Article().paginate(size=5)
    return view('articles.index', articles=articles[0], pagination=articles[1])

There are a few important things to note about the syntax of the
templating system:

-  To write variables simply wrap ``{{ }}`` around the variable name.
-  Due to the way the template compiler works if the variable is one
   'generated' by a for loop, like the ``article`` variable in the
   example above, it must also be wrapped by ``$ $``.

Builder.py (CLI)
^^^^^^^^^^^^^^^^
The builder (CLI) can be called by executing the following:

::

    python builder.py [command name] --[option]=[value] [argument]

Below is an exhaustive list of all commands currently implemented:

+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| Command  | Option | Accepted values                 | Argument | Accepted values | Role                                                                                                                                |
+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| setup    | None   | None                            | None     | None            | Creates the required directories for the application to work (controllers, models, storage, middleware and templates)               |
+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| generate | type   | model, middleware or controller | name     | str             | according to the PEP 8 naming scheme (snake case). Please note that the file names are converted to camel case for the class names. |
+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| migrate  | None   | None                            | None     | None            | Generates (and executes) the SQL to create the tables for all developer created models.                                             |
+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| drop     | None   | None                            | None     | None            | Drops all tables that correspond to defined model classes.                                                                          |
+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+
| auth     | None   | None                            | None     | None            | Generates the authentication scaffold for the given project.                                                                        |
+----------+--------+---------------------------------+----------+-----------------+-------------------------------------------------------------------------------------------------------------------------------------+

Config
^^^^^^
Detailed below is an exhaustive list of configuaration options that can be put in 'config.py':

+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Variable name   | Type | Function                                                                                                                                                                                                                                                                                          |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ROOT_DIR        | Str  | This is the root directory of the project. This value should not be changed.                                                                                                                                                                                                                      |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| MIDDLEWARE      | List | A list of middleware to be registered. To register a middleware file dot notation should be used. For example to register a middleware file called 'user_middleware' that is in the 'middleware' directory the following should be added to the list (as a string): 'middleware.user_middleeware' |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| NO_AUTH         | List | A list of routes that do not require the user to be authenticated.                                                                                                                                                                                                                                |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| PYTHON_TO_REGEX | Dict | A dictionary that contains mappings from route parameter definitions to regular expression. Any new mapping added can be used in the router.                                                                                                                                                      |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| URL             | Str  | The root URL of the application.                                                                                                                                                                                                                                                                  |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DATABASE        | Dict | A dictionary containing the configuration settings for the database.                                                                                                                                                                                                                              |
+-----------------+------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Demo App
^^^^^^^^
Please see `here <https://github.com/MattJMLewis/dragonfly-demo>`__ for further code from the example project.
