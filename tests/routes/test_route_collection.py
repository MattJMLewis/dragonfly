from unittest import TestCase
from dragonfly.routes.route_collection import RouteCollection
from dragonfly.exceptions import MethodDoesNotExist, InvalidControllerMethod

class TestRouteCollection(TestCase):

    def setUp(self):
        self.route_collection = RouteCollection()

    def test_static_add(self):
        self.route_collection.add('testing', 'TestController@testing', 'GET')
        self.assertEqual(self.route_collection.match_route('testing', 'GET'), ('TestController@testing', {}))

    def test_dynamic_add(self):
        self.route_collection.add('testing/<id:int>', 'TestController@testing', 'GET')
        self.assertEqual(self.route_collection.match_route('testing/1', 'GET'), ('TestController@testing', {'id': 1}))

    def test_multiple_dynamic_add(self):
        self.route_collection.add('testing/<id:int>/<name:str>', 'TestController@testing', 'GET')
        self.assertEqual(self.route_collection.match_route('testing/1/test', 'GET'), ('TestController@testing', {'id': 1, 'name': 'test'}))

    def test_erroneous_method(self):
        with self.assertRaises(MethodDoesNotExist):
            self.route_collection.add('testing', 'TestController@testing', 'TESTING')

        with self.assertRaises(MethodDoesNotExist):
            self.route_collection.add('testing/<id:int>', 'TestController@testing', 'TESTING')

    def test_erroneous_action(self):
        with self.assertRaises(InvalidControllerMethod):
            self.route_collection.add('testing', 'InvalidController#Method', 'GET')
