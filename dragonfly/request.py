import cgi
from urllib import parse
from http.cookies import SimpleCookie
from dragonfly.constants import DATA_METHODS


class Request:

    def __init__(self, environ):

        if environ is not None:
            self.path = environ.get('PATH_INFO')[1:]
            self.method = environ.get('REQUEST_METHOD')
            self.query_string = environ.get('QUERY_STRING')
            self.remote_address = environ.get('REMOTE_ADDR')

            self.headers = {k: v for k, v in environ.items() if k.startswith('HTTP_')}

            try:
                cookie = SimpleCookie()
                cookie.load(self.headers['HTTP_COOKIE'])

                self.cookies = {k: v.value for k, v in cookie.items()}
            except KeyError:
                self.cookies = {}

            self.wsgi = {'url_scheme': environ.get('wsgi.url_scheme'), 'input': environ.get('wsgi.input'),
                         'errors': environ.get('wsgi.errors'), }

            self.uri = self.headers['HTTP_HOST'] + '/' + self.path
            self.environ = environ
        else:
            self.environ = None

    def get_data(self):
        if self.environ is not None:
            if self.method in DATA_METHODS:
                environ_copy = self.environ
                environ_copy['QUERY_STRING'] = ''

                field_storage = cgi.FieldStorage(fp=environ_copy['wsgi.input'], environ=environ_copy, keep_blank_values=True)

                field_dict = {}

                for key in field_storage.keys():
                    field_dict[key] = field_storage[key].value

                return field_dict

            elif self.method == 'GET':
                if self.query_string is not None:
                    return parse.parse_qs(self.query_string)

        return None

    def update_environ(self, new_environ):
        self.__init__(new_environ)


request = Request(None)
