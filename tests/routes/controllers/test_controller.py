from dragonfly import Controller
from dragonfly import Response


class TestController(Controller):

    def test(self):
        return Response()
