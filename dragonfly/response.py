from dragonfly.constants import REASON_PHRASES


class Response:
    """
    The base :class:`Response` class that is readable by the WSGI server.

    Parameters
    ----------
    :param content: The content that will be delivered to the user. This defaults to empty.
    :type content: str

    :param content_type: The MIME type. This defaults to 'text/html'.
    :type content_type: str

    :param status_code: The HTTP status code. This defaults to success (200).
    :type status_code: int

    :param reason_phrase: A written meaning of the HTTP status code. If left as `None` the reason phrase will be
    chosen from a pre-determined list.
    :type reason_phrase: int
    """

    def __init__(self, content='', content_type='text/html', status_code=200, reason_phrase=None):

        self.content_type = content_type
        self.original_content = content
        self.content = content
        self.status = None

        self.set_content()
        self.set_status(status_code, reason_phrase)

        self.headers = [
            ('Content-type', self.content_type),
            ('Content-Length', str(len(self.content)))
        ]

    def set_content(self):
        """
        Converts the given content to bytes.
        """
        try:
            self.content = bytes(str(self.original_content), 'utf-8')
        except:
            raise Exception("Content cannot be converted to a string")

    def set_status(self, status_code, reason_phrase):
        """
        Sets the status of the :class:`Response` object. If the ``reason_phrase`` is ``None`` then a reason phrase that corresponds
        to the status code will be retrieved from a ``constants`` file.

        :param status_code: The status code of the response.
        :type status_code: int

        :param reason_phrase: The reason phrase to accompany the status code. This can be `None`.
        :type reason_phrase: str
        """

        reason_phrase = REASON_PHRASES[status_code] if reason_phrase is None else reason_phrase
        self.status = f"{status_code} {reason_phrase}"

    def header(self, field_name, field_value):
        """
        Updates an existing header or creates a new one.

        :param field_name: The header field name.
        :type field_name: str

        :param field_value: The header field value.
        :type field_value: str
        """

        loc = next((i for i, v in enumerate(self.headers) if v[0] == field_name), None)
        new_header = (field_name, field_value)
        if loc is None:
            self.headers.append(new_header)
        else:
            self.headers[loc] = new_header

    def translate_deferred(self, deferred):
        """
        Merges the given `DeferredResponse` object to this `Response` instance.

        :param deferred: The `DeferredResponse` object.
        :type deferred: DeferredResponse
        """

        for key, value in deferred.headers.items():
            self.header(key, value)


class ErrorResponse(Response):
    """
    A `Response` object that returns an error page.

    :param error_message: The error message.
    :type error_message: str

    :param status_code: The status code.
    :type status_code: int
    """

    def __init__(self, error_message, status_code):

        generated_html = \
            f'''
        <div id="main">
                <div class="fof">
                        <h1>Error {status_code}</h1>
                        <h5>{error_message}</h5>
                </div>
        </div>
        <style>
        '''
        super().__init__(content=generated_html, content_type='text/html', status_code=status_code)


class DeferredResponse:
    """
    Allows headers for a future response to be set before it exists.

    This singleton enables attributes of any `Response` object returned in the normal fashion, i.e through the
    `dispatch_route` method, to be set before it exists. The primary use of this class would be in the `before` method
    of a middleware.

    To do:
    - Support modifying content and status.
    """

    def __init__(self):
        self.headers = {}

    def header(self, field_name, field_value):
        """Define the headers to be set on the real :class:`Response` object."""
        self.headers[field_name] = field_value


deferred_response = DeferredResponse()
