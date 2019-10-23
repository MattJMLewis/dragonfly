import importlib
import os
import platform
import re

from config import ROOT_DIR

from dragonfly.request import request
from dragonfly.response import Response

INDENT = "	"

class TemplateLang:

	def __init__(self, original, line):
		self.original = original
		self.line = line
		self.role = self.__identify_line(original)
		self.indent = 0

	def set_indent(self, indent):
		self.indent = indent

	@property
	def python(self):
		return self.__convert()

	def __convert(self):
		stripped = self.original[3:-3]

		if self.role == 1:
			return f"''' + str({self.__convert_var(stripped)}) + '''"

		elif self.role == 2:
			return f"''' + str({stripped}) + '''"

		elif self.role == 3:
			words = stripped.split()
			if words[0] == 'if' or words[0] == 'elif':
				for i, word in enumerate(words):
					if i % 2 == 1:
						words[i] = self.__convert_var(word)

				statement = " ".join(words)

			elif words[0] == 'for':
				statement = f"for {words[1]} in {self.__convert_var(words[3])}"

			indent_level = self.indent + 1
			return f"'''\n{INDENT*indent_level}{statement}:\n{INDENT*(indent_level + 1)}template += '''"

		elif self.role == 5:
			return f"'''\n{INDENT * self.indent}else:\n{INDENT * (self.indent + 1)}template += '''"
		else:
			return ''


	@staticmethod
	def __convert_var(var):
		if "'" in var or '"' in var:
			return var
		else:
			if "." in var:
				split = var.split('.')
				return f"kwargs['{split[0]}'].{split[1]}"
			else:
				return f"kwargs['{var}']"

	@staticmethod
	def __identify_line(line):

		if re.match('{{[^{}*]*}}', line) is not None:
			return 1

		if re.match('{\[[^{}*]*]}', line) is not None:
			return 2

		if re.match("{%[^{}]*}}", line) is not None:
			return 3

		if re.match("{{[^{}]*%}", line) is not None:
			return 4

class Node:

	def __init__(self, data):
		self.data = data
		self.children = []

	def add_child(self, data):
		self.children.append(Node(data))


class Stack:

	def __init__(self):
		self.items = []

	def push(self, item):
		self.items.append(item)

	def push_many(self, items):
		self.items.extend(items)

	def pop(self):
		return self.items.pop()


class Converter:

	def __init__(self):
		self.__lines = []
		self.__original_html = []
		self.file = None

	def __load(self):
		with open(self.file) as f:
			self.__original_html = f.readlines()

		for i, line in enumerate(self.__original_html):
			result = re.findall("({{[^{}*]*}}|{%[^{}]*}}|{{[^{}]*%}|{\[[^{}*]*]})", line)
			if result:
				self.__lines.append(TemplateLang(result[0], i))

	@staticmethod
	def __get_integers(flat_list):
		integer_index = []
		for i, item in enumerate(flat_list):
			if isinstance(item, int):
				integer_index.append([i, item])

		print(flat_list)
		print(integer_index)

		return integer_index

	def convert(self, file):
		self.file = file
		self.__load()

		lists = [[]]
		current_list = 0

		for line in self.__lines:
			if line.role == 1 or line.role == 2:
				line.set_indent(current_list)
				lists[current_list].append(line)
			elif line.role == 3:
				lists[current_list].append(current_list + 1)
				current_list += 1
				line.set_indent(current_list - 1)
				lists.append([line])
			elif line.role == 4:
				lists[current_list].append(line)
				current_list -= 1

		i = len(lists) - 1
		while i >= 0:
			has_integers = self.__get_integers(lists[i])
			while has_integers:
				to_add = 0
				for integer in has_integers:
					duplicate_list = lists[i]

					index = integer[0] + to_add

					duplicate_list.pop(index)

					duplicate_list[index:index] = lists[integer[1]]

					to_add += len(lists[integer[1]])

					lists[i] = duplicate_list

				has_integers = self.__get_integers(lists[i])

			i -= 1

		flat_list = lists[0]
		html = ''

		html += f"def get_html(kwargs):\n"
		html += f"{INDENT}template = '''\n"

		line_no = [l.line for l in flat_list]

		for i, line in enumerate(self.__original_html):
			if i in line_no:
				template_lang = flat_list[line_no.index(i)]

				line = line.replace(template_lang.original, template_lang.python)

			html += line

		html += "'''"
		html += f"\n{INDENT}return template"

		return html


class View:

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
		return Response(self.html)

	def __write_to_file(self):

		html = Converter().convert(self.file_path)
		try:
			with open(self.template_path, 'w+') as f:
				f.writelines(html)
		except FileNotFoundError:
			os.makedirs(self.template_path.rpartition(self.slash)[0], exist_ok=True)

			with open(self.template_path, 'w+') as f:
				f.writelines(html)


def view(view, **kwargs):
	return View(view, **kwargs).make()
