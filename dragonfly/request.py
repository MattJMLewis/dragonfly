import cgi
from http.cookies import SimpleCookie
from urllib import parse

from dragonfly.constants import DATA_METHODS


class Request:
    """The request object is a class representation of the WSGI environ dictionary"""

    def __init__(self, environ):
        """
        Extracts the useful values in the environ dictionary.

        :param environ: The environ dictionary from the WSGI server.
        :type environ: dict
        """
        self.__field_dict = None

        if environ is not None:

            # Important environ values
            self.path = environ.get('PATH_INFO')[1:]
            self.method = environ.get('REQUEST_METHOD')
            self.query_string = environ.get('QUERY_STRING')
            self.remote_address = environ.get('REMOTE_ADDR')

            # Store all items in environ dict which start with 'HTTP_'
            self.headers = {k: v for k, v in environ.items() if k.startswith('HTTP_')}

            try:
                # Try to get all the cookies in the eviron
                cookie = SimpleCookie()
                cookie.load(self.headers['HTTP_COOKIE'])

                self.cookies = {k: v.value for k, v in cookie.items()}
            except KeyError:
                self.cookies = {}

            self.wsgi = {'url_scheme': environ.get('wsgi.url_scheme'), 'input': environ.get('wsgi.input'),
                         'errors': environ.get('wsgi.errors'), }

            self.base_uri = 'http://' + self.headers['HTTP_HOST']
            self.uri = self.headers['HTTP_HOST'] + '/' + self.path
            self.environ = environ
        else:
            self.environ = None

    def get_data(self):
        """
        Gets any from data/query strings from the given request

        :return: A dictionary containing the given data
        :rtype: dict
        """
        # Allows request data to be cached until new request occurs. This means data can be retrieved more than once.
        if self.__field_dict is not None:
            return self.__field_dict

        if self.environ is not None:
            if self.method in DATA_METHODS:

                environ_copy = self.environ
                environ_copy['QUERY_STRING'] = ''

                # Get all field data and store in dict
                field_storage = cgi.FieldStorage(fp=environ_copy['wsgi.input'], environ=environ_copy,
                                                 keep_blank_values=False)

                field_dict = {}

                for key in field_storage.keys():
                    field_dict[key] = field_storage[key].value

                self.__field_dict = field_dict

                return field_dict

            # If get request may have query strings which need to be retrieved
            elif self.method == 'GET':
                if self.query_string is not None:
                    return parse.parse_qs(self.query_string)

        return {}

    def update_environ(self, new_environ):
        """
        Updates the request object (singleton) with new data

        :param new_environ: The new environ dictionary
        :type new_environ: dict
        """
        # Reset request with new data
        self.__init__(new_environ)


request = Request(None)
