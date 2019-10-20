from unittest import TestCase
from dragonfly.route import Router
from dragonfly.constants import PYTHON_TO_REGEX


class TestRouter(TestCase):

    def setUp(self):
    	self.router = Router()
   	
   	def test_add_route(self):

