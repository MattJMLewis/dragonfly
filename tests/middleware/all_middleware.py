from dragonfly.response import Response


class AllMiddleware:
    actions = '*'

    def before(self):
        return Response('before (*)')

    def after(self):
        return Response('after (*)')
