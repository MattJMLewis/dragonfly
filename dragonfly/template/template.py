import re
import os
import platform
import importlib

from dragonfly.response import Response
from dragonfly.request import request
from config import ROOT_DIR


INDENT = "    "

LINE = 1
VAR = 2
OPEN_CONTROL = 3
CLOSE_CONTROL = 4
ELSE_CONTROL = 5

class Line:

    def __init__(self, line, indent):
        self.line = line
        self.matches = None
        self.identity = self.__identify()
        self.indent = indent

    def __str__(self):
        return f"{self.matches} | {self.identity} | {self.indent}"

    def __identify(self):
        variable_matches = re.findall("({{[^{}*]*}})", self.line)
        open_ctrl_matches = re.findall("(@[^(]{1,4}\(.*\))", self.line)
        else_ctrl_matches = re.findall("@else", self.line)
        close_ctr_matches = re.findall("(@endif)|(@endfor)", self.line)

        if variable_matches:
            self.matches = variable_matches
            return VAR

        elif open_ctrl_matches:
            self.matches = open_ctrl_matches[0]

            return OPEN_CONTROL

        elif else_ctrl_matches:
            self.matches = else_ctrl_matches[0]

            return ELSE_CONTROL

        elif close_ctr_matches:
            self.matches = close_ctr_matches[0]
            return CLOSE_CONTROL
        else:
            return LINE

    def reduce_indent(self):
        self.indent -= 1

    def to_python(self):

        if self.identity == LINE:
            return self.line

        elif self.identity == VAR:
            python = self.line

            for match in self.matches:
                python = python.replace(match, f"''' + str({self.__fix_variable(match[3:-3])}) + '''")

            return python

        elif self.identity == OPEN_CONTROL:

            in_brackets = re.findall("@(.{1,4})\((.*)\)", self.matches)

            clause = in_brackets[0][0]
            statement = in_brackets[0][1]
            words = statement.split(' ')

            if "for" not in clause:
                for i, word in enumerate(words):
                    if not (word[0] == "'" or word[0] == '"') and not (word[-1] == "'" or word[-1] == '"'):
                        if i != 1:
                            try:
                                int(word)
                            except ValueError:
                                words[i] = self.__fix_variable(word)

            else:
                if "range" in words[2]:

                    range_words = []
                    range_words.append(words[2].split('(', 1)[1][:-1])
                    range_words.append(words[3][:-1])

                    for i, word in enumerate(range_words):
                        if not (word[0] == "'" or word[0] == '"') and not (word[-1] == "'" or word[-1] == '"'):
                            try:
                                int(word)
                            except ValueError:
                                range_words[i] = self.__fix_variable(word)

                    return f"'''\n{INDENT * self.indent}for {words[0]} in range({range_words[0]}, {range_words[1]}):\n{INDENT * (self.indent + 1)}template += '''"
                else:
                    words[2] = self.__fix_variable(words[2])

            statement = " ".join(words)

            python = f"'''\n{INDENT * self.indent}{clause} {statement}:\n{INDENT * (self.indent + 1)}template += '''"

            return python

        elif self.identity == ELSE_CONTROL:

            python = f"'''\n{INDENT * self.indent}else:\n{INDENT * (self.indent + 1)}template += '''"

            return python

        elif self.identity == CLOSE_CONTROL:
            return f"'''\n{INDENT * self.indent}template += '''\n"

    @staticmethod
    def __fix_variable(variable):
        if variable.count('$') == 2:
            return variable[1:-1]
        else:
            try:
                before, after = variable.split('.', 1)
                return f"kwargs['{before}'].{after}"
            except ValueError:
                try:
                    before, after = variable.split('[', 1)
                    return f"kwargs['{before}'][{after}"
                except ValueError:
                    return f"kwargs['{variable}']"

class Template:

    def __init__(self, file):
        self.file = file
        self.lines = self.__to_lines()
        self.objects = []

    def __to_lines(self):
        with open(self.file) as f:
            lines = f.readlines()

        return lines

    def convert(self):
        indent = 1

        for line in self.lines:
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

            self.objects.append(line_object)

        html = f"def get_html(kwargs):\n{INDENT}template = '''"

        for l in self.objects:
            python = l.to_python()
            if python:
                html += python

        html += f"'''\n{INDENT}return template\n"

        return html


class View:
    """
    Returns a HTML version of the requested template.
    The class first finds the desired view. If a pre-compiled python version of the template does not exist or is out
    of date, the class will generate one. Otherwise it imports the compiled python file and runs the ``get_html``
    method, passing in any variables that the user.py has given to the constructor (via ``**kwargs``). It then returns a
    :class:`Response <dragonfly.response.Response>` with this HTML.
    :param view: The view to return
    :type view: str
    """

    def __init__(self, view, **kwargs):

        self.slash = '/'
        if platform.system() == 'Windows':
            self.slash = '\\'

        local_loc = view.replace(".", self.slash)

        self.file_path = os.path.join(ROOT_DIR, f"views{self.slash}" + local_loc + '.html')
        self.template_path = os.path.join(ROOT_DIR, f"storage{self.slash}templates{self.slash}{local_loc}.py")

        try:
            os.path.getmtime(self.template_path)
        except FileNotFoundError:
            self.__write_to_file()

        if os.path.getmtime(self.file_path) > os.path.getmtime(self.template_path):
            self.__write_to_file()

        kwargs['request'] = request
        self.html = importlib.import_module(f"storage.templates.{view}").get_html(kwargs)

    def make(self):
        """
        Returns a response with the generated HTML.
        :return: The response
        :rtype: Response
        """
        return Response(self.html)

    def __write_to_file(self):
        """
        Write the generated template file from the template.
        """
        html = Template(self.file_path).convert()
        try:
            with open(self.template_path, 'w+') as f:
                f.writelines(html)
        except FileNotFoundError:
            os.makedirs(self.template_path.rpartition(self.slash)[0], exist_ok=True)

            with open(self.template_path, 'w+') as f:
                f.writelines(html)


def view(view, **kwargs):
    return View(view, **kwargs).make()
