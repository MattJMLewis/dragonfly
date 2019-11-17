import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
MIDDLEWARE = []
PYTHON_TO_REGEX = {"int": "([0-9]+)", "str": "(.+)"}
URL = "http://localhost:8080"

DATABASE = {
    'user': 'testing',
    'passwd': 'testing',
    'host': '127.0.0.1',
    'db': 'testing'
}