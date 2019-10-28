import importlib
import os
import platform
import re

from config import ROOT_DIR

from dragonfly.request import request
from dragonfly.response import Response
from dragonfly.template.classes import Snippet, Clause, Stack, identify, OPEN, CLOSE, VAR, IF, END_IF, FOR, END_FOR, \
    ELSE, ELSE_IF


class Parser:
    """
    The :class:`Parser` reads from the given template file and converts it to a flat list of :class:`Snippet` objects.

    :param file: The file to convert.
    :type file: str
    """

    def __init__(self, file):
        self.file = file
        self.__lines = []
        self.__stack_lines = []
        self.__processed_lines = []
        self.__recursions = 0

    def __to_lines(self):
        """
        Read each line in the template file and append all lines that contain ``{{``, ``}}``, ``{%`, `%}`` to ``self.lines``
        """
        with open(self.file) as f:
            lines = f.readlines()

        for line in lines:
            self.__lines.append(re.findall("({{[^{}*]*}}|{%[^{}]*}}|{{[^{}]*%})", line))

    def __to_processed_lines(self):
        """
        Converts the templating lines (e.g {{ var }}) to either a :class:`Clause` or :class:`Snippet` object.
        """
        sorting_stack = Stack()

        for i, line in enumerate(self.__lines):
            line_number = i + 1

            for value in line:
                identity = identify(value)

                if identity is VAR or identity is OPEN:
                    sorting_stack.push(Snippet(value, line_number))

                if identity is CLOSE:
                    open_found = False
                    popped_values = []

                    while not open_found:
                        popped_value = sorting_stack.pop()
                        popped_values.append(popped_value)

                        if popped_value.type is OPEN:
                            open_found = True

                    popped_values.reverse()
                    popped_values.append(Snippet(value, line_number))
                    sorting_stack.push(Clause(popped_values[1:-1], popped_values[0], popped_values[-1]))

        self.__stack_lines = sorting_stack.items

    def __generate_from_clause(self, clause):
        """
        As :class:`Snippet`s or other :class:`Clause`s may be contained in a :class:`Clause` a recursive function is needed to 'squish' the
        :class:`Clause`. To preserve the location (and indentation) of a contained object it's depth is incremented.

        :param clause: The Clause to squish.
        :type clause: Clause
        """
        for item in clause.content:
            item.increment_depth()
            if isinstance(item, Clause):
                to_add = item.to_snippets()
                self.__processed_lines.append(to_add[0])
                self.__processed_lines.append(self.__generate_from_clause(item))
                self.__processed_lines.append(to_add[1])
            else:
                self.__processed_lines.append(item)

    def __to_flat_list(self):
        """
        Converts the 3D object list to a flat list of snippets.
        """
        for line in self.__stack_lines:
            if isinstance(line, Snippet):
                self.__processed_lines.append(line)
            else:
                to_add = line.to_snippets()
                self.__processed_lines.append(to_add[0])
                self.__generate_from_clause(line)
                self.__processed_lines.append(to_add[1])

    def parse(self):
        """Parses the given file to a list of :class:`Snippet`s"""
        self.__to_lines()
        self.__to_processed_lines()
        self.__to_flat_list()
        return list(filter(None, self.__processed_lines))


class Converter:
    """
    The :class:`Converter` converts the given template file to the ``.py`` equivalent. This enables control structures and
    variables to be easily injected into HTML.

    The :class:`Converter` calls the :class:`Parser` class first before generating the ``.py`` file.

    :param file: The template file to convert.
    :type file: str

    """
    def __init__(self, file):
        self.values = Parser(file).parse()
        self.html = []

        with open(file) as f:
            self.lines = f.readlines()

    def fix_clause(self, snippet_str):
        """
        Fixes clauses in ``if`` and ``else if`` statements.

        :param snippet_str: The templating language to fix.
        :type snippet_str: str

        :return dict
        """
        to_fix = re.findall("%[^%*]*%", snippet_str)

        for word in to_fix:
            snippet_str = snippet_str.replace(word, f"kwargs['{word[1:-1]}']")

        return snippet_str

    def convert(self):
        """
        Converts the template HTML to python.
        """
        for i, line in enumerate(self.lines):
            to_convert = [l for l in self.values if (l.line - 1) == i]

            if to_convert:
                if len(to_convert) == 1:
                    snippet = to_convert[0]

                    indent = "    " * (snippet.depth + 1)
                    clause_indent = "    " * (snippet.depth + 2)

                    if snippet.python_type is VAR:
                        before, after = snippet.stp_content.split('.', 1)

                        var_str = f"str(kwargs['{before}'].{after})"

                        if re.findall("%[^%*]*%", snippet.stp_content):
                            var_str = f"str({snippet.stp_content[1:-1]})"

                        line = line.replace(snippet.content, f"''' + {var_str} + '''")

                    if snippet.python_type is IF:
                        self.html[i - 1] = self.html[i - 1].rstrip() + "'''\n"
                        fixed_clause = self.fix_clause(snippet.stp_content)
                        line = f"{indent}{fixed_clause}:\n{clause_indent}template += '''\n"

                    if snippet.python_type is ELSE:
                        self.html[i - 1] = self.html[i - 1].rstrip() + "'''\n"
                        indent = "     " * (snippet.depth - 1)
                        clause_indent = "    " * snippet.depth
                        line = f"{indent}else:\n{clause_indent}template += '''\n"

                    if snippet.python_type is ELSE_IF:
                        self.html[i - 1] = self.html[i - 1].rstrip() + "'''\n"
                        indent = "     " * (snippet.depth - 1)
                        clause_indent = "    " * snippet.depth
                        fixed_clause = self.fix_clause(snippet.stp_content)
                        line = f"{indent}{fixed_clause}:\n{clause_indent}template += '''\n"

                    if snippet.python_type is END_IF:
                        line = f"'''\n{indent}template += '''\n"

                    if snippet.python_type is FOR:
                        iterable = snippet.stp_content.split()[3]
                        snippet.stp_content = snippet.stp_content.replace(iterable, f"kwargs['{iterable}']")
                        self.html[i - 1] = self.html[i - 1].rstrip() + "'''\n"
                        line = f"{indent}{snippet.stp_content}:\n{clause_indent}template += '''"

                    if snippet.python_type is END_FOR:
                        line = f"'''\n{indent}template += '''\n"

                else:
                    for snippet in to_convert:
                        line = line.replace(snippet.content, f"''' + str({snippet.stp_content}) + '''")

            self.html.append(line)

        self.html.insert(0, "    template = '''\n")
        self.html.insert(0, "def get_html(kwargs):\n")
        self.html.append("    '''\n")
        self.html.append("    return template")

        return self.html


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
        html = Converter(self.file_path).convert()
        try:
            with open(self.template_path, 'w+') as f:
                f.writelines(html)
        except FileNotFoundError:
            os.makedirs(self.template_path.rpartition(self.slash)[0], exist_ok=True)

            with open(self.template_path, 'w+') as f:
                f.writelines(html)


