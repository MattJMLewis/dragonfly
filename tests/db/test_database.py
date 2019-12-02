from unittest import TestCase
from dragonfly.db.database import DB


class TestDB(TestCase):

    def setUp(self):
        self.database = DB().table('testing')
        self.database.custom_sql("CREATE TABLE testing (id INT AUTO_INCREMENT PRIMARY KEY, string VARCHAR(255))")
        self.database.custom_sql(
            'INSERT INTO testing (string) VALUES ("Test"), ("Test 1"), ("Test 2"), ("Test 3"), ("Test 4")')

    def tearDown(self):
        self.database.custom_sql("DROP TABLE testing")

    def test_select(self):
        self.assertEqual(self.database.select('id').first(), {'id': 1})

    def test_where(self):
        self.assertEqual(self.database.where('string', '=', 'Test').first(), {'id': 1, 'string': 'Test'})

    def test_multiple_where(self):
        self.assertEqual(self.database.multiple_where({'string': 'Test', 'id': 1}).first(), {'id': 1, 'string': 'Test'})

    def test_get(self):
        self.assertEqual(self.database.get(), (
        {'id': 1, 'string': 'Test'}, {'id': 2, 'string': 'Test 1'}, {'id': 3, 'string': 'Test 2'},
        {'id': 4, 'string': 'Test 3'}, {'id': 5, 'string': 'Test 4'}))

    def test_first(self):
        self.assertEqual(self.database.first(), {'id': 1, 'string': 'Test'})

    def test_chunk(self):
        self.assertEqual(self.database.chunk(2, 2), ({'id': 3, 'string': 'Test 2'}, {'id': 4, 'string': 'Test 3'}))

    def test_update(self):
        self.database.where('id', '=', 1).update({'string': 'Updated'})
        self.assertEqual(self.database.where('id', '=', 1).first(), {'id': 1, 'string': 'Updated'})

    def test_delete(self):
        self.database.where('id', '=', 1).delete()
        self.assertEqual(self.database.where('id', '=', 1).first(), None)

    def test_insert(self):
        self.database.insert({'string': 'Testing 5'})
        self.assertEqual(self.database.where('id', '=', 6).first(), {'id': 6, 'string': 'Testing 5'})

