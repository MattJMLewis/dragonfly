from config import MIDDLEWARE
from dragonfly.response import Response
import importlib


class MiddlewareController:
    """Loads all registered middleware and controls their execution."""

    def __init__(self):

        # Middleware the user has defined in config file.
        self.__registered_middleware = []

        # Middleware that should run on all routes.
        self.__all_middleware = []

        # Middleware that has been retrieved and executed once and is thus cached. It is stored under the action it
        # executes on.
        self.__cached_middleware = {}

        self.__register_middleware()

    def __register_middleware(self):
        """Register the middleware that is defined in the config file."""
        for middleware in MIDDLEWARE:
            middleware_cls_name = ''.join(x.capitalize() or '_' for x in middleware.split('.')[-1:][0].split('_'))
            middleware = getattr(importlib.import_module(middleware), middleware_cls_name)()

            if middleware.actions == '*':
                self.__all_middleware.append(middleware)
            else:
                self.__registered_middleware.append(middleware)

    def run_before(self, action):
        """
        Run all the before methods on middleware that are assigned to the given action.

        :param action: The action currently being executed.
        :type action: str

        :return: If a ``Response`` is generated return this
        :rtype: :class:`Response <dragonfly.response.Response>`
        """
        try:
            # Try get all cached middleware __on the given action
            for middleware in self.__cached_middleware[action]:
                middleware_response = middleware.before()

                # If returns a response return this
                if isinstance(middleware_response, Response):
                    return middleware_response

        except KeyError:
            # Generate cache and execute function again
            self.__create_action_cache(action)
            return self.run_before(action)

        # Execute all middleware
        for middleware in self.__all_middleware:
            middleware_response = middleware.before()

            if isinstance(middleware_response, Response):
                return middleware_response

    def run_after(self, action, response):
        """
        Run all the after methods on the middleware that are assigned to the given action.

        :param action: The action currently being executed.
        :type action: str

        :param response: The ``Response`` that the router has generated. If the 'after' function accepts the ``Response`` class it is passed on (to allow for its modification).
        :type response: :class:`Response <dragonfly.response.Response>`

        :return: If a ``Response`` is generated return this
        :rtype: :class:`Response <dragonfly.response.Response>`
        """

        # Same as previous function
        try:
            for middleware in self.__cached_middleware[action]:
                # Check if after function accepts a response. If it doesn't run without passing it in
                try:
                    middleware_response = middleware.after(Response)
                except TypeError:
                    middleware_response = middleware.after()

                if isinstance(middleware_response, Response):
                    return middleware_response

        except KeyError:
            self.__create_action_cache(action)
            return self.run_after(action, response)

        for middleware in self.__all_middleware:
            try:
                middleware_response = middleware.after(Response)
            except TypeError:
                middleware_response = middleware.after()

            if isinstance(middleware_response, Response):
                return middleware_response

    def __create_action_cache(self, action):
        """
        This function generates a cache of middleware on the given action. This system prevents any unnecessary
        storage of unused middleware.

        :param action: The action to create a cache for.
        :type: str
        """
        self.__cached_middleware[action] = []

        # Get all middleware that are assigned to the given action and store in a dictionary
        for middleware in self.__registered_middleware:
            if action in middleware.actions:
                self.__cached_middleware[action].append(middleware)
                self.__registered_middleware.remove(middleware)


middleware_controller = MiddlewareController()