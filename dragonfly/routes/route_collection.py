from dragonfly.routes.route_rule import RouteRule
from dragonfly.constants import METHODS


class RouteCollection:
    """
    A way to store registered routes.
    """

    def __init__(self):
        self.static_routes = {}
        self.dynamic_routes = {}

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
            if isinstance(method, list):
                route_rule = RouteRule(uri)
                for method in METHODS:
                    self.dynamic_routes[method][route_rule] = action
            else:
                # Store the dynamic route as a `RouteRule` object and assign it the value of its action.
                self.dynamic_routes[method][RouteRule(uri)] = action
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
            for route, action in self.dynamic_routes[method].items():
                match = route.match(uri)
                if match:
                    return action, match

            return None, {}

    @staticmethod
    def __is_dynamic(uri):
        left = uri.count("<")
        right = uri.count(">")

        return left == right and left >= 1
