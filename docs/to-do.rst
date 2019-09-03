To do
=====

.. danger::
	- [X] Fix :class:`Request` so that it does not crash when cookies are not present.
	- [X] Prevent MySQL injection on :class:`DB`.


.. caution::
    - Production server.
    - [X] Make all single-use classes into singletons. This is done via module level variables
    - [X] Reduce length of namespace for classes.
    - [X] Add a ``RedirectResponse``.
    - ``create`` & ``delete`` pk auto detection works for non composite keys. How to solve for composite?
    - Add ``created_at``, ``updated_at`` and ``id`` fields to class by default.
    - [X] Add a ``url`` method that extracts the base url of the site from the config.
    - Add a ``{{ csrf_token }}`` template variable to prevent CSRF attacks.
    - Add a built in auth system (including auth middleware, :class:`User` class and a way to easily retrieve the authenticated :class:`User`).
    - Look at Laravel/Django and add more features to :class:`Response` & :class:`Request` and doc blocks.

.. attention::
	- Add a caching system
	- Is there a way to speed up SQL commands?
	- Make :class:`View` syntax more natural.
	- Allow the user to specify a secondary database connection and use that on a model.
