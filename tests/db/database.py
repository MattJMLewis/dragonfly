from unittest import TestCase
from dragonfly.db.database import DB


class TestDB(TestCase):

	def setUp(self):
		self.database = DB().table('testing')
		self.database.custom_sql("CREATE TABLE testing (id INT AUTO_INCREMENT PRIMARY KEY, string VARCHAR(255))")
		self.database.custom_sql('INSERT INTO testing (string) VALUES ("Test"), ("Test 1"), ("Test 2"), ("Test 3"), ("Test 4")')

	def tearDown(self):
		self.database.custom_sql("DROP TABLE testing")

	def test_select(self):
		self.assertEqual(self.database.select('id').first(), {'id': 1})

	def test_where(self):
		self.assertEqual(self.database.where('string', '=', 'Test').first(), {'id': 1, 'string': 'Test'})

	def test_multiple_where(self):
		self.assertEqual(self.database.multiple_where({'string': 'Test', 'id': 1}).first(), {'id': 1, 'string': 'Test'})

	def test_get(self):
		pass

	def test_first(self):
		pass

	def test_chunk(self):
		pass

	def test_update(self):
		pass

	def test_delete(self):
		pass

	def test_insert(self):
		pass
