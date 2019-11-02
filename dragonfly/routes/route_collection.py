from collections import defaultdict

from dragonfly.constants import METHODS
from dragonfly.routes.route_rule import RouteRule


class RouteCollection:
    """
    A way to store registered routes.
    """

    def __init__(self):
        self.static_routes = {}
        self.dynamic_routes = defaultdict(dict)

        for method in METHODS:
            self.static_routes[method] = {}
            self.dynamic_routes[method] = {}

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
        # Determine if the route is dynamic (contains a route parameter e.g <id:int> )
        if self.__is_dynamic(uri):
            # If we return a list of methods to add (this is primarily used for the `.any()` function on the router.
            key_list = uri.split('<', 1)[0].split('/')
            del key_list[-1]

            if isinstance(method, list):
                route_rule = RouteRule(uri)

                for method in METHODS:
                    slug_dict = self.dynamic_routes[method]

                    for key in key_list:
                        slug_dict = slug_dict.setdefault(key, {})

                    slug_dict[route_rule] = action

            else:
                slug_dict = self.dynamic_routes[method]

                for key in key_list:
                    slug_dict = slug_dict.setdefault(key, {})

                slug_dict[RouteRule(uri)] = action

        else:
            if isinstance(method, list):
                # Used for the `.any()` function on the router.
                for method in METHODS:
                    self.static_routes[method][uri] = action
            else:
                # Store the static route in a simple dictionary.
                self.static_routes[method][uri] = action

    def match_route(self, uri, method):
        """
        Match the given route using its URI and method. First we check if it is a static route before checking all
        dynamic routes
        """
        try:
            return self.static_routes[method][uri], {}
        except KeyError:
            # Potential refactor here. Have a dictionary that contains slugs and slugs of slugs etc... e.g
            # dynamic_routes['/articles']['/comments'] <- which would then contain a list of route rules to match.
            key_list = uri.split('/')
            slug_dict = self.dynamic_routes[method]

            for key in key_list:
                try:
                    slug_dict = slug_dict[key]
                except KeyError:
                    pass

            # Differentiate between iterating too far or nothing being found

            for route, action in slug_dict.items():
                if isinstance(route, RouteRule):
                    match = route.match(uri)
                    if match:
                        return action, match

            return None, {}

    @staticmethod
    def __is_dynamic(uri):
        has_left = uri.count("<")
        has_right = uri.count(">")

        return has_left == has_right and has_left >= 1
