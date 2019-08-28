import re

VAR = 1
OPEN = 2
CLOSE = 3

IF = 4
END_IF = 5

ELSE = 6
ELSE_IF = 7

FOR = 8
END_FOR = 9


def identify(string):
    """
    Identifies what clause the string is e.g opening.

    :param string: The string to identify.
    :type string: str

    :return: The identity of the clause.
    :rtype: int
    """

    if re.match('{{[^{}*]*}}', string) is not None:
        return VAR

    if re.match("{%[^{}]*}}", string) is not None:
        return OPEN

    if re.match("{{[^{}]*%}", string) is not None:
        return CLOSE


def identify_python(string):
    """
    Identifies the 'python' in the template.

    :param string: The string to identify.
    :type string: str

    :return: The identity of the python, if any.
    :rtype: int
    """

    if "end if" in string:
        return END_IF
    elif "end for" in string:
        return END_FOR
    elif "for " in string:
        return FOR
    elif "elif" in string:
        return ELSE_IF
    elif "if " in string:
        return IF
    elif "else" in string:
        return ELSE
    else:
        return VAR


class Stack:
    """
    A simple stack structure for the `Parser`
    """

    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def push_many(self, items):
        self.items.extend(items)

    def pop(self):
        return self.items.pop()


class Snippet:
    """
    A `Snippet` represents a line of templating code e.g if, etc...
    """

    def __init__(self, content, line):
        self.content = content
        self.stp_content = content[3:-3]
        self.line = line
        self.type = identify(content)
        self.python_type = identify_python(content)
        self.depth = 0

    def increment_depth(self):
        self.depth += 1


class Clause:
    """
    A `Clause` represents an entire command structure. This includes the `Snippet`s for its opening and closing tags and
    any `Clause` or `Snippet` contained within it.
    """

    def __init__(self, content, opening_line, closing_line):
        self.content = content
        self.open = opening_line
        self.close = closing_line
        self.line_numbers = (self.open.line, self.close.line)
        self.type = None
        self.depth = 0

    def increment_depth(self):
        self.depth += 1
        self.open.increment_depth()
        self.close.increment_depth()

        for item in self.content:
            item.increment_depth()

    def to_snippets(self):
        return [
            self.open,
            self.close
        ]
