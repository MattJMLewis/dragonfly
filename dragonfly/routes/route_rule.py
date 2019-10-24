import re
from config import PYTHON_TO_REGEX


class RouteRule:
    """
    Used to register dynamic routes. Allows for an easy check of whether a given route matches a dynamic route.
    """

    def __init__(self, uri):
        self.__groups = []
        self.converted_uri = self.__convert_to_regex(uri)

    def match(self, uri):
        """
        Matches the given route to an action and extracts any router parameters.

        :param uri: The URI to match.
        :type uri: str

        :return: A dictionary containing the the action and any route parameters.
        :rtype: :class:`dict`
        """

        match = re.fullmatch(self.converted_uri, uri)

        if match is None:
            return False
        else:
            for i in range(len(self.__groups)):
                self.__groups[i][1] = match.group(i + 1)

            arg_dict = {}
            for el in self.__groups:
                if el[2] == 'int':
                    arg_dict[el[0]] = int(el[1])
                else:
                    arg_dict[el[0]] = str(el[1])

            return arg_dict

    def __convert_to_regex(self, uri):
        matches = re.findall("(<[^<]+:[^>]+>)", uri)
        for match in matches:
            uri = re.sub(match, self.__map_to_regex, uri)

        return uri

    def __map_to_regex(self, match):
        name, type = match.group(0).split(":")
        self.__groups.append([name[1:], None, type[:-1]])
        return PYTHON_TO_REGEX[type[:-1]]
