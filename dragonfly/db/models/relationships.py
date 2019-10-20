'''
def servers(self):
	return hasMany(self, 'server')
'''
import importlib

class hasMany:

	def __init__(self, has, belongs, foregin_key=None):
		self.has = has
		self.belongs = belongs

		belongs = getattr(importlib.import_module(f"models.{has}"), has.capitalize())()
		if not foregin_key:
			foregin_key = has