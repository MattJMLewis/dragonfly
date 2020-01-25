from unittest import TestCase
from dragonfly.routes.route_rule import RouteRule


class TestRouteRule(TestCase):

    def test_static_route(self):
        route_rule = RouteRule('test')

        self.assertEqual(route_rule.match('test'), {})
        self.assertEqual(route_rule.match('testing'), False)

    def test_dynamic_route(self):
        route_rule = RouteRule('test/<id:int>')

        self.assertEqual(route_rule.match('test/1'), {'id': 1})
        self.assertEqual(route_rule.match('testing'), False)

    # This is a boundary test
    def test_multiple_dynamic_route(self):
        route_rule = RouteRule('test/<id:int>/<name:str>')

        self.assertEqual(route_rule.match('test/1/test'), {'id': 1, 'name': 'test'})
        self.assertEqual(route_rule.match('testing'), False)
