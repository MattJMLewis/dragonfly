import importlib
from dragonfly.db.database import DB


class hasMany:

	def __init__(self, has, this_key=None, has_key=None):

		self.has_value = has
		self.this_key = this_key
		self.has_key = has_key

		self.this = None
		self.has = None
		self.values = None

		self.index = 0

	def delayed_init(self, values, meta):

		self.index = 0

		self.has = getattr(importlib.import_module(f"models.{self.has_value}"), self.has_value.capitalize())()

		if self.has_key is None:
			self.has_key = meta['table_name'][:-1] + '_id'

		if self.this_key is None:
			self.this_key = 'id'

		self.values = self.has.where(self.has_key, '=', values[self.this_key]).get()

		return self

	def __iter__(self):
		return self

	def __next__(self):
		try:
			result = self.values[self.index]
		except IndexError:
			raise StopIteration

		self.index += 1

		return result

	def __getitem__(self, index):
		return self.values[index]

	def __len__(self):
		return len(self.values)


class belongsTo:

	def __init__(self, belongs):
		pass