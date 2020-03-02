from dragonfly.response import Response


class TestMiddleware:
    actions = 'testing'

    def before(self):
        return Response('before (testing)')

    def after(self):
        return Response('after (testing)')
