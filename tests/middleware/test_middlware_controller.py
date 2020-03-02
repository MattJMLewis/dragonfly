from unittest import TestCase
from dragonfly.middleware.middleware_controller import MiddlewareController

class TestBuilder(TestCase):

    def setUp(self):
        self.middleware_controller = MiddlewareController()

    def test_before(self):

        result = self.middleware_controller.run_before('all_routes')
        self.assertEqual(result.content, b'before (*)')

        result = self.middleware_controller.run_before('testing')
        self.assertEqual(result.content, b'before (testing)')

    def test_after(self):

        result = self.middleware_controller.run_after('all_routes', 'response')
        self.assertEqual(result.content, b'after (*)')

        result = self.middleware_controller.run_after('testing', 'response')
        self.assertEqual(result.content, b'after (testing)')
