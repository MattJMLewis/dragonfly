import re

class Node:

	def __init__(self, data):
		self.data = data
		self.children = {}

	def add_child(self, title, data):
		self.children[title] = Node(data)


class Converter:

	def __init__(self):
		self.__lines = []
		self.__tree = Node('')
		self.file = None


	def __load():
		with open(self.file) as f:
			lines = f.readlines()

		for i, line in enumerate(lines):
			result = re.findall("({{[^{}*]*}}|{%[^{}]*}}|{{[^{}]*%})", line)
			if result:
				self.__lines.append([i - 1, result])


	def convert(self, file):
		self.file = file
		self.__load()

		for 
		
           

Converter().convert('edit.html')