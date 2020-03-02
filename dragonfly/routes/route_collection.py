from collections import defaultdict

from dragonfly.constants import METHODS
from dragonfly.routes.route_rule import RouteRule
from dragonfly.exceptions import MethodDoesNotExist, InvalidControllerMethod

import re

class RouteCollection:
    """
    A way to store registered routes.
    """

    def __init__(self):
        self.__static_routes = {}
        self.__dynamic_routes = defaultdict(dict)

        for method in METHODS:
            self.__static_routes[method] = {}
            self.__dynamic_routes[method] = {}

    def add(self, uri, action, method):
        """
        Add a new route to either the static or dynamic routes dictionary.

        :param uri: The route uri
        :type uri: str

        :param action: The route action
        :type action: str

        :param method: The route HTTP method
        :type method: str
        """

        if method not in METHODS:
            raise MethodDoesNotExist(f"{method} is not a valid HTTP method")

        if re.fullmatch("(.+@.+)", action) is None:
            raise InvalidControllerMethod(f"{action} does not conform to the controller method naming scheme. See docs "
                                          f"for more info")

        # Determine if the route is dynamic (contains a route parameter e.g <id:int> )
        if self.__is_dynamic(uri):
            # Split url at '/' and '<'
            url_list = uri.split('<', 1)[0].split('/')
            del url_list[-1]

            # If we return a list of methods to add (this is primarily used for the `.any()` function on the router.
            if isinstance(method, list):
                route_rule = RouteRule(uri)

                for method in METHODS:
                    slug_dict = self.__dynamic_routes[method]

                    for url in url_list:
                        # Iterate over each part of url and add a new dictionary (as a value) to the previously defined
                        # dictionary with the current url part as the key
                        slug_dict = slug_dict.setdefault(url, {})

                    # Store the route rule, as the key, in the final dictionary (that corresponds to the final slug in
                    # the static part of the URL) with the value as the action it corresponds to
                    slug_dict[route_rule] = action
            else:
                # Same as above but for one HTTP method
                slug_dict = self.__dynamic_routes[method]

                for url in url_list:
                    slug_dict = slug_dict.setdefault(url, {})

                slug_dict[RouteRule(uri)] = action

        else:
            if isinstance(method, list):
                # Used for the `.any()` function on the router.
                for method in METHODS:
                    self.__static_routes[method][uri] = action
            else:
                # Store the static route in a simple dictionary.
                self.__static_routes[method][uri] = action

    def match_route(self, uri, method):
        """
        Match the given route using its URI and method. First we check if it is a static route before checking all
        dynamic routes.

        :param uri: The URI to match
        :type uri: str

        :param method: The HTTP method
        :type method: str

        :return: Any matching routes
        :type: dict
        """

        # See if static route first before trying dynamic route dictionary
        try:
            return self.__static_routes[method][uri], {}
        except KeyError:
            url_list = uri.split('/')
            slug_dict = self.__dynamic_routes[method]

            # Iterate over each slug in the URL and find the corresponding dictionary until failure
            for url in url_list:
                try:
                    slug_dict = slug_dict[url]
                except KeyError:
                    pass

            for route, action in slug_dict.items():
                # Ensure value found is a RouteRule (and not another dictionary)
                if isinstance(route, RouteRule):
                    match = route.match(uri)
                    if match:
                        return action, match

            return None, {}

    @staticmethod
    def __is_dynamic(uri):
        """
        Determines if the URI is dynamic.

        :param uri: The URI to check
        :type uri: str

        :return: If the URI is dynamic or not.
        :rtype: bool
        """

        has_left = uri.count("<")
        has_right = uri.count(">")

        return has_left == has_right and has_left >= 1
