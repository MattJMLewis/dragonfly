from unittest import TestCase
from dragonfly.db.database_migrator import DatabaseMigrator


class TestDatabaseMigrator(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbm = DatabaseMigrator(path='tests/models')
        print(cls.dbm.tables)

    def test_table_name(self):
        self.assertEqual(self.dbm.tables['different_name'], ([], 'CREATE TABLE different_name \n)'))

    def test_id(self):
        self.assertEqual(self.dbm.tables['ids'], ([], 'CREATE TABLE ids (\ncreated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\nupdated_at TIMESTAMP ON UPDATE NOW() DEFAULT NOW()\n)'))

    def test_timestamps(self):
        self.assertEqual(self.dbm.tables['timestamps'], ([], 'CREATE TABLE timestamps \n)'))

    def test_null(self):
        self.assertEqual(self.dbm.tables['nulls'], ([], 'CREATE TABLE nulls (\nstring CHAR(255) NULL\n)'))

    def test_primary_key(self):
        self.assertEqual(self.dbm.tables['primarykeys'], ([], 'CREATE TABLE primarykeys (\nstring CHAR(255) PRIMARY KEY,\nanother_string CHAR(255),\nPRIMARY KEY (another_string)\n)'))

    def test_unique(self):
        self.assertEqual(self.dbm.tables['uniques'], ([], 'CREATE TABLE uniques (\nstring CHAR(255) UNIQUE\n)'))

    def test_default(self):
        self.assertEqual(self.dbm.tables['defaults'], ([], "CREATE TABLE defaults (\nstring CHAR(255) DEFAULT 'testing',\nsecond_string CHAR(255) DEFAULT 1\n)"))

    def test_all_fields(self):
        print(self.dbm.tables['fields'])
