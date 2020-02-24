from unittest import TestCase
from dragonfly.routes.router import Router
from dragonfly.request import request
from dragonfly.response import Response, ErrorResponse
import os


class TestRouter(TestCase):


	def setUp(self):

		self.router = Router()

		request.update_environ({
			'HTTP_HOST': 'localhost:8080',
			'REQUEST_METHOD': 'GET',
			'PATH_INFO': '/',
			'QUERY_STRING': '',
			'REMOTE_ADDR': '127.0.0.1',
		})

		self.router.get('', 'TestController@test')

	def test_dispatch_route(self):
		response = self.router.dispatch_route()
		self.assertIsInstance(response, Response)

	def test_erroneous_dispatch_route(self):
		# Shows the router deals errors by returning an error response

		request.path = '/error'

		response = self.router.dispatch_route()

		self.assertIsInstance(response, ErrorResponse)

