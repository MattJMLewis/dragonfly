from unittest import TestCase
from dragonfly.routes.route_collection import RouteCollection
from dragonfly.constants import METHODS


class TestRouteCollection(TestCase):

    def setUp(self):
        self.route_collection = RouteCollection()
        self.route_collection.add('testing/<id:int>', 'TestController@test', 'GET')
        self.route_collection.add('home', 'TestController@test', 'GET')

    def test_add(self):
        self.assertEqual(bool(self.route_collection.dynamic_routes['GET']), True)
        self.assertEqual(bool(self.route_collection.static_routes['GET']), True)

    def test_match_route(self):

        # Test static routes when they are both present and not present
        self.assertTupleEqual(self.route_collection.match_route('home', 'GET'), ('TestController@test', {}))
        self.assertTupleEqual(self.route_collection.match_route('homes', 'POST'), (None, {}))

        # Test dynamic routes when they are both present and not present
        self.assertTupleEqual(self.route_collection.match_route('testing/1', 'GET'), ('TestController@test', {'id': 1}))
        self.assertTupleEqual(self.route_collection.match_route('testing/invalid_route', 'GET'), (None, {}))
