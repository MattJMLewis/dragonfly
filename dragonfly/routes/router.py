import importlib
import re

from dragonfly.constants import METHODS, DATA_METHODS
from dragonfly.middleware.middleware_controller import middleware_controller
from dragonfly.request import request
from dragonfly.response import Response, ErrorResponse, deferred_response
from dragonfly.routes.route_collection import RouteCollection


def to_snake(name):
    """
    From StackOverflow https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class Router:
    """
    Routes the given route to the defined ``Controller``and returns its
    generated :class:`Response <dragonfly.response.Response>`.
    """

    def __init__(self):
        self.__routes = RouteCollection()

    def add_route(self, uri, action, method):
        """
        Adds a route to the `RouteCollection` object.

        :param uri: The URI of the route
        :type uri: str

        :param action: The action of the route e.g 'HomeController@home'
        :type action: str

        :param method: The HTTP method verb e.g 'GET'
        :type method: str
        """

        self.__routes.add(uri, action, method)

    def dispatch_route(self):
        """
        Dispatches the appropriate route based on the request method and path.
        """

        # See if there is a hidden input on the request that changes the request method.
        request_data = request.get_data()

        try:
            method = request_data['_method'].upper()
            if method in ['PUT', 'PATCH', 'DELETE']:
                request.method = method

            del request_data['_method']
        except KeyError:
            pass

        action, parameters = self.__routes.match_route(request.path, request.method)

        # If no route is found
        if action is None:
            return ErrorResponse("Route not found", status_code=404)
        else:
            # Run any `before` methods on the registered middleware.
            middleware_response = middleware_controller.run_before(action)

            # Check if they returned a `Response` and return that (thus cancelling the rest of the routing).
            if isinstance(middleware_response, Response):
                return middleware_response

            # Import the correct controller, pass in request object (if request is singleton this can be removed...).
            controller_file, controller_function_name = action.split("@")
            controller_class = getattr(importlib.import_module(f"controllers.{to_snake(controller_file)}"),
                                       controller_file)
            controller_class = controller_class()
            controller_function = getattr(controller_class, controller_function_name)

            try:
                del request_data['csrf_token']
            except KeyError:
                pass

            # If there is a possibility that the given request method could send data e.g POST, try and fetch it.
            if request.method in DATA_METHODS:
                parameters['request_data'] = request_data

            # Run the appropriate function on the controller
            response = controller_function(**parameters)

            # Modify the response using the `DeferredResponse` singleton.
            response.translate_deferred(deferred_response)

            # Run any `after` methods on the registered middleware.
            middleware_response = middleware_controller.run_after(action, response)

            # Check if they returned a `Response` and return that (thus cancelling the rest of the routing).
            if isinstance(middleware_response, Response):
                return middleware_response

            return response

    def get(self, uri, action):
        self.add_route(uri, action, 'GET')

    def post(self, uri, action):
        self.add_route(uri, action, 'POST')

    def put(self, uri, action):
        self.add_route(uri, action, 'PUT')

    def patch(self, uri, action):
        self.add_route(uri, action, 'PATCH')

    def options(self, uri, action):
        self.add_route(uri, action, 'OPTIONS')

    def delete(self, uri, action):
        self.add_route(uri, action, 'DELETE')

    def any(self, uri, action):
        self.add_route(uri, action, METHODS)

    def resource(self, uri, controller):
        self.get(uri, f"{controller}@index")
        self.get(f"{uri}/<id:int>", f"{controller}@show")

        self.get(f"{uri}/create", f"{controller}@create")
        self.post(uri, f"{controller}@store")

        self.get(f"{uri}/<id:int>/edit", f"{controller}@edit")
        self.put(f"{uri}/<id:int>", f"{controller}@update")

        self.delete(f"{uri}/<id:int>", f"{controller}@delete")
