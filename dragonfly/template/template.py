import importlib
import os
import platform
import re

from config import ROOT_DIR
from dragonfly.auth import Auth
from dragonfly.request import request
from dragonfly.response import Response
from dragonfly.utils import Utils

INDENT = "    "

# For clarity
LINE = 1
VAR = 2
OPEN_CONTROL = 3
CLOSE_CONTROL = 4
ELSE_CONTROL = 5


# Template -> View (combination of HTML + Python)

class Line:
    """Object to represent a single line in the template file"""

    def __init__(self, line, indent):
        """
        Identifies and breaks down line into constituent components

        :param line: The line to be represented
        :type: str

        :param indent: THe current indent level (1 represents one tab)
        :type: int
        """
        self.line = line
        self.__matches = None
        self.identity = self.__identify()
        self.__indent = indent

    def __str__(self):
        return f"{self.__matches} | {self.identity} | {self.__indent}"

    def __identify(self):
        """Identifies the type of dragonfly templating in the template file"""
        variable_matches = re.findall("({{[^{}*]*}})", self.line)
        open_ctrl_matches = re.findall("(@[^(]{1,4}\(.*\))", self.line)
        else_ctrl_matches = re.findall("@else", self.line)
        close_ctr_matches = re.findall("(@endif)|(@endfor)", self.line)

        if variable_matches:
            self.__matches = variable_matches
            return VAR

        elif open_ctrl_matches:
            self.__matches = open_ctrl_matches[0]
            return OPEN_CONTROL

        elif else_ctrl_matches:
            self.__matches = else_ctrl_matches[0]
            return ELSE_CONTROL

        elif close_ctr_matches:
            self.__matches = close_ctr_matches[0]
            return CLOSE_CONTROL
        else:
            return LINE

    def reduce_indent(self):
        """Reduce the indent of the :class:`Line <dragonfly.template.Template>` by 1"""
        self.__indent -= 1

    def to_python(self):
        """Converts the :class:`Line <dragonfly.template.Template>` to its Python equivalent"""
        if self.identity == LINE:
            return self.line

        elif self.identity == VAR:
            python = self.line

            for match in self.__matches:
                # Replace the match (templating code) with Python (close template string, concatenate the chosen
                # variable and reopen string)
                python = python.replace(match, f"''' + str({self.__fix_variable(match[3:-3])}) + '''")

            return python

        elif self.identity == OPEN_CONTROL:

            in_brackets = re.findall("@(.{1,4})\((.*)\)", self.__matches)

            # Get the first word of the statement (e.g if, for, etc...)
            clause = in_brackets[0][0]

            # Anything after the first word
            statement = in_brackets[0][1]
            words = statement.split(' ')

            if "for" not in clause:
                for i, word in enumerate(words):
                    # Check that the word is a string and thus should be left alone
                    if not (word[0] == "'" or word[0] == '"') and not (word[-1] == "'" or word[-1] == '"'):
                        # Check that this is not the comparison operator (i != 1) and it isn't a Python term
                        if i != 1 and word not in ['None', 'True', 'False', 'is', 'not']:
                            # Try to convert to an integer, if not possible i.e it is a variable, 'fix' it
                            try:
                                int(word)
                            except ValueError:
                                words[i] = self.__fix_variable(word)

            else:
                # Edge case
                if "range" in words[2]:

                    range_words = []

                    # This is the first word in the range statement
                    range_words.append(words[2].split('(', 1)[1][:-1])
                    # This is the second
                    range_words.append(words[3][:-1])

                    for i, word in enumerate(range_words):
                        # Like above, ensure this is not a string
                        if not (word[0] == "'" or word[0] == '"') and not (word[-1] == "'" or word[-1] == '"'):
                            try:
                                int(word)
                            except ValueError:
                                range_words[i] = self.__fix_variable(word)

                    # Generate the Python equivalent of the for loop (with the correct indentation)
                    return f"'''\n{INDENT * self.__indent}for {words[0]} in range({range_words[0]}, {range_words[1]}):\n{INDENT * (self.__indent + 1)}template += '''"
                else:
                    # Normal for loop, just fix the iterable being iterated over
                    words[2] = self.__fix_variable(words[2])

            # Rejoin all the modified words
            statement = " ".join(words)

            # Generate the correct python using the extracted variables
            python = f"'''\n{INDENT * self.__indent}{clause} {statement}:\n{INDENT * (self.__indent + 1)}template += '''"

            return python

        elif self.identity == ELSE_CONTROL:

            python = f"'''\n{INDENT * self.__indent}else:\n{INDENT * (self.__indent + 1)}template += '''"

            return python

        elif self.identity == CLOSE_CONTROL:
            return f"'''\n{INDENT * self.__indent}template += '''\n"

    @staticmethod
    def __fix_variable(variable):
        """
        Fixes the given variable and converts it to a callable variable.

        :param variable: The variable to convert
        :type: str

        :return: The converted variable
        :type: str
        """
        # Determine if the variable is generated in a for loop and thus does not need to be retrieved from kwargs
        # dictionary
        if variable.count('$') == 2:
            return variable[1:-1]
        else:
            try:
                # Convert any calls __on an object e.g object.action to kwargs['object'].action
                before, after = variable.split('.', 1)
                return f"kwargs['{before}'].{after}"
            except ValueError:
                try:
                    # If above not possible see if can convert to kwargs['list'][index]
                    before, after = variable.split('[', 1)
                    return f"kwargs['{before}'][{after}"
                except ValueError:
                    # If none of the above it must be just a simple variable
                    return f"kwargs['{variable}']"


class Converter:

    def __init__(self, file):
        self.__file = file
        self.__lines = self.__to_lines()
        self.__objects = []

    def __to_lines(self):
        with open(self.__file) as f:
            lines = f.readlines()

        return lines

    def convert(self):
        """
        Convert the given file to Python.

        :return: The Python code.
        :rtype: str
        """
        indent = 1

        for line in self.__lines:
            line_object = Line(line, indent)

            if line_object.identity == OPEN_CONTROL:
                if "elif" in line_object.line:
                    line_object.reduce_indent()
                else:
                    indent += 1

            elif line_object.identity == ELSE_CONTROL:
                if "else" in line_object.line:
                    line_object.reduce_indent()
                else:
                    indent += 1

            elif line_object.identity == CLOSE_CONTROL:
                indent -= 1
                line_object.reduce_indent()

            self.__objects.append(line_object)

        python = f"def get_html(kwargs):\n{INDENT}template = '''"

        for l in self.__objects:
            l_python = l.to_python()
            if l_python:
                python += l_python

        python += f"'''\n{INDENT}return template\n"

        return python


class View:
    """
    Returns a HTML version (view) of the requested template.
    The class first attempts to locate the deisred view. If a pre-compiled python version of the template does not exist or is out
    of date, the class will generate one. Otherwise it imports the compiled python file and runs the ``get_html``
    method, passing in any variables that the user.py has given to the constructor (via ``**kwargs``). It then returns a
    :class:`Response <dragonfly.response.Response>` with this HTML.
    :param template: The view to return
    :type template: str
    """

    def __init__(self, template, **kwargs):
        """
        Loads the chosen template and converts to HTML (a view)

        :param template: The location of the template in the 'templates' directory (using dot notation for the path e.g.
        'articles.show'
        :param kwargs: Any variables to pass into the view
        """
        # Cross platform compatibility
        self.__slash = '/'
        if platform.system() == 'Windows':
            self.__slash = '\\'

        # Get an actual __file path
        local_loc = template.replace(".", self.__slash)

        self.__template_path = os.path.join(ROOT_DIR, f"templates{self.__slash}" + local_loc + '.html')
        self.__view_path = os.path.join(ROOT_DIR, f"storage{self.__slash}views{self.__slash}{local_loc}.py")

        # Try to get last modified time, if not present __file does not exist
        try:
            os.path.getmtime(self.__view_path)
        except FileNotFoundError:
            self.__write_to_file()

        # If template updated after compiled view then regenerated python and write to __file
        if os.path.getmtime(self.__template_path) > os.path.getmtime(self.__view_path):
            self.__write_to_file()

        # Add in useful features to template by default
        kwargs['request'] = request
        kwargs['Auth'] = Auth
        kwargs['Utils'] = Utils

        # Retrieve the HTML from the compiled template
        self.__html = importlib.import_module(f"storage.views.{template}").get_html(kwargs)

    def make(self):
        """
        Returns a response with the generated HTML.

        :return: The ``Response``
        :rtype: :class:`Response <dragonfly.response.Response>`
        """
        return Response(self.__html)

    def __write_to_file(self):
        """
        Write the compiled template to the file (view).
        """
        html = Converter(self.__template_path).convert()
        try:
            with open(self.__view_path, 'w+') as f:
                f.writelines(html)
        except FileNotFoundError:
            # Generate needed directories if not present
            os.makedirs(self.__view_path.rpartition(self.__slash)[0], exist_ok=True)

            with open(self.__view_path, 'w+') as f:
                f.writelines(html)


def view(view, **kwargs):
    """
    Returns the given view with the given variables added.

    :param view: The view to retrieve
    :rtype: str

    :param kwargs: Any variables to pass to the view
    :rtype: dict

    :return: The generated HTML
    :rtype: str
    """
    return View(view, **kwargs).make()
