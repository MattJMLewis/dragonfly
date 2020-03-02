import re
from config import PYTHON_TO_REGEX


class RouteRule:
    """
    Data structure to store dynamic routes. Allows for an easy check of whether a given route matches a dynamic route.
    """

    def __init__(self, uri):

        self.__route_parameters = []

        # Firstly convert the given URI to a regex expression that can easily be checked. Also generate the needed
        # structures for any expected route parameters
        self.__converted_uri = self.__convert_to_regex(uri)

    def match(self, uri):
        """
        Matches the given route to an action and extracts any router parameters.

        :param uri: The URI to match.
        :type uri: str

        :return: A dictionary containing the the action and any route parameters.
        :rtype: dict
        """

        match = re.fullmatch(self.__converted_uri, uri)

        if match is None:
            return False

        for i in range(len(self.__route_parameters)):
            self.__route_parameters[i][1] = match.group(i + 1)

        arg_dict = {}
        for el in self.__route_parameters:
            if el[2] == 'int':
                arg_dict[el[0]] = int(el[1])
            else:
                arg_dict[el[0]] = str(el[1])

        return arg_dict

    def __convert_to_regex(self, uri):
        """
        Converts the given URI to regex.

        :param uri: The URI to convert
        :rtype: str

        :return: The converted URI
        :rtype: str
        """
        matches = re.findall("(<[^<]+:[^>]+>)", uri)
        for match in matches:
            # Substitute the match with the corresponding regex
            uri = re.sub(match, self.__map_to_regex, uri)

        return uri

    def __map_to_regex(self, match):
        """
        Finds the regex equivalent of the route parameter declaration as well generating the appropriate data structures
        for the route parameters.

        :param match: The route parameter declaration

        :return: The regex equivalent of the given route parameter declaration
        :rtype: str
        """
        # Split the parameter '<id:int>' to two strings
        name, type = match.group(0).split(":")

        # Add a tuple to the route parameters list containg the name and type of parameter to expect
        self.__route_parameters.append([name[1:], None, type[:-1]])

        # Get corresponding regex from config.py
        return PYTHON_TO_REGEX[type[:-1]]
