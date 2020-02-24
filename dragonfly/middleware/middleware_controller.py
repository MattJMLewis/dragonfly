from config import MIDDLEWARE
from dragonfly.response import Response
import importlib


class MiddlewareController:
    """Compiles all registered middleware and controls their execution."""

    def __init__(self):

        self.registered_middleware = []
        self.all_middleware = []
        self.cached_middleware = {}

        self.register_middleware()

    def register_middleware(self):
        """Register the middleware that is defined in the config file."""
        for middleware in MIDDLEWARE:
            middleware_cls_name = ''.join(x.capitalize() or '_' for x in middleware.split('.')[-1:][0].split('_'))
            middleware = getattr(importlib.import_module(middleware), middleware_cls_name)()

            if middleware.actions == '*':
                self.all_middleware.append(middleware)
            else:
                self.registered_middleware.append(middleware)

    def run_before(self, action):
        """
        Run all the before methods on middleware that are assigned to the given action

        :param action: The action currently being executed.
        """
        try:
            for middleware in self.cached_middleware[action]:
                middleware_response = middleware.before()

                if isinstance(middleware_response, Response):
                    return middleware_response

        except KeyError:
            self.create_action_cache(action)
            return self.run_before(action)

        for middleware in self.all_middleware:
            middleware_response = middleware.before()

            if isinstance(middleware_response, Response):
                return middleware_response

    def run_after(self, action, response):
        """Run all the after methods on middleware that are assigned to the given action."""
        try:
            for middleware in self.cached_middleware[action]:
                middleware_response = middleware.after()

                if isinstance(middleware_response, Response):
                    return middleware_response

        except KeyError:
            self.create_action_cache(action)
            return self.run_after(action, response)

        for middleware in self.all_middleware:
            middleware_response = middleware.after()

            if isinstance(middleware_response, Response):
                return middleware_response

    def create_action_cache(self, action):
        """Create a cache of middleware that are currently in use."""
        self.cached_middleware[action] = []

        for middleware in self.registered_middleware:
            if action in middleware.actions:
                self.cached_middleware[action].append(middleware)
                self.registered_middleware.remove(middleware)


middleware_controller = MiddlewareController()