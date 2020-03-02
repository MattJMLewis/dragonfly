import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
MIDDLEWARE = ['tests.middleware.test_middleware', 'tests.middleware.all_middleware'] # These are only needed for testing
PYTHON_TO_REGEX = {"int": "([0-9]+)", "str": "(.+)"}
URL = "http://localhost:8080"

DATABASE = {
    'user': 'dragonfly',
    'passwd': 'password',
    'host': '127.0.0.1',
    'db': 'dragonfly_testing'
}