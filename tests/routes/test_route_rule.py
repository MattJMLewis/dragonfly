from unittest import TestCase
from dragonfly.routes.route_rule import RouteRule
from dragonfly.constants import PYTHON_TO_REGEX


class TestRouteRuleCollection(TestCase):

    def test_match(self):

        # We need to test for all different types
        for key, value in PYTHON_TO_REGEX.items():
            values = PYTHON_TO_REGEX[key]
            route_rule = RouteRule(values[0])

            self.assertDictEqual(route_rule.match(str(values[1])), {'var': values[1]})

        # Test that any non matching routes return False
        route_rule = RouteRule('testing/<test:int>')
        self.assertEqual(route_rule.match('testing/invalid'), False)
