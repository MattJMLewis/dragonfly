from unittest import TestCase
from dragonfly.routes.router import Router


class TestRouter(TestCase):

	def setUp(self):
		self.router = Router()

	def test_add_route(self):
		self.router.get('get', 'TestController@get')
		self.router.post('post', 'TestController@post')
		self.router.put('put', 'TestController@put')
		self.router.patch('patch', 'TestController@patch')
		self.router.options('options', 'TestController@options')
		self.router.delete('delete', 'TestController@delete')
		self.router.any('any', 'TestController')


