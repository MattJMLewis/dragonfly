from config import MIDDLEWARE
from dragonfly.response import Response
import importlib


class MiddlewareController:
    """Compiles all registered middleware and controls their execution."""

    def __init__(self):

        self.registered_middleware = []
        self.register_middleware()
        self.cached_middleware = {}

    def register_middleware(self):
        """Register the middleware that is defined in the config file."""
        for middleware in MIDDLEWARE:
            middleware_cls_name = ''.join(x.capitalize() or '_' for x in middleware.split('.')[-1:][0].split('_'))
            self.registered_middleware.append(getattr(importlib.import_module(middleware), middleware_cls_name)())

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

    def create_action_cache(self, action):
        """Create a cache of middleware that are currently in use."""
        self.cached_middleware[action] = []

        for middleware in self.registered_middleware:
            if action in middleware.actions:
                self.cached_middleware[action].append(middleware)


middleware_controller = MiddlewareController()

