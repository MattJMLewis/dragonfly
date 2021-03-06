from unittest import TestCase
from dragonfly.template.template import Converter
import importlib


class TestTemplate(TestCase):

    def test_convert(self):
        res = Converter('test.html').convert()

    def test_erroneous_if(self):
        res = Converter('if_error.html').convert()

        with open('if_error.py', 'w+') as f:
            f.truncate(0)
            f.writelines(res)

        with self.assertRaises(SyntaxError):
            html = importlib.import_module("if_error").get_html(var=1)

    def test_erroneous_for(self):
        res = Converter('for_error.html').convert()

        with open('for_error.py', 'w+') as f:
            f.truncate(0)
            f.writelines(res)

        with self.assertRaises(KeyError):
            arg_dict = {'items': [1, 2, 3]}
            html = importlib.import_module("for_error").get_html(arg_dict)
