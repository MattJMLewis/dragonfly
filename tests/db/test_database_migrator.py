from unittest import TestCase
from dragonfly.db.database_migrator import DatabaseMigrator


class TestDatabaseMigrator(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbm = DatabaseMigrator(path='tests/models')

    def test_table_name(self):
        self.assertEqual(self.dbm.tables['different_name'], ([], 'CREATE TABLE different_name \n)'))

    def test_id(self):
        self.assertEqual(self.dbm.tables['ids'], ([],
                                                  'CREATE TABLE ids (\ncreated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\nupdated_at TIMESTAMP ON UPDATE NOW() NOT NULL DEFAULT NOW()\n)'))

    def test_timestamps(self):
        self.assertEqual(self.dbm.tables['timestamps'], ([], 'CREATE TABLE timestamps \n)'))

    def test_null(self):
        self.assertEqual(self.dbm.tables['nulls'], ([], 'CREATE TABLE nulls (\nstring CHAR NULL\n)'))

    def test_primary_key(self):
        self.assertEqual(self.dbm.tables['primarykeys'], (
            [], 'CREATE TABLE primarykeys (\nstring CHAR NOT NULL PRIMARY KEY,\nanother_string CHAR NOT NULL\n)'))

    def test_unique(self):
        self.assertEqual(self.dbm.tables['uniques'], ([], 'CREATE TABLE uniques (\nstring CHAR NOT NULL UNIQUE\n)'))

    def test_default(self):
        self.assertEqual(self.dbm.tables['defaults'], ([],
                                                       "CREATE TABLE defaults (\nstring CHAR NOT NULL DEFAULT 'testing',\nsecond_string CHAR NOT NULL DEFAULT 1\n)"))

    def test_all_fields(self):
        self.assertEqual(self.dbm.tables['fields'], ([],
                                                     "CREATE TABLE fields (\nempty_bit BIT NOT NULL,\nnbit BIT(10) NOT NULL,\nempty_tiny_int TINYINT NOT NULL,\nntiny_int TINYINT(10) NOT NULL,\nnbool BOOLEAN NOT NULL,\nempty_small_int SMALLINT NOT NULL,\nnsmall_int SMALLINT(10) NOT NULL,\nempty_medium_int MEDIUMINT NOT NULL,\nnmedium_int MEDIUMINT(10) NOT NULL,\nempty_int INT NOT NULL,\nnint INT(10) NOT NULL,\nempty_big_int BIGINT NOT NULL,\nnbig_int BIGINT(10) NOT NULL,\nempty_decimal DECIMAL NOT NULL,\nndecimal DECIMAL(5, 2) NOT NULL,\nempty_float FLOAT NOT NULL,\nnfloat FLOAT(10) NOT NULL,\nempty_double DOUBLE NOT NULL,\nndouble DOUBLE(5, 2) NOT NULL,\nndate DATE NOT NULL,\nempty_datetime DATETIME NOT NULL,\nndatetime DATETIME(6) NOT NULL,\nempty_timestamp TIMESTAMP NOT NULL,\nntimestamp TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,\nnn_timestamp TIMESTAMP(6) NULL,\nempty_time TIME NOT NULL,\nntime TIME(6) NOT NULL,\nnyear YEAR NOT NULL,\nempty_varchar VARCHAR(15) NOT NULL,\nnvarchar VARCHAR(10) NOT NULL,\nempty_char CHAR NOT NULL,\nnchar CHAR(255) NOT NULL,\nempty_binary VARBINARY(15) NOT NULL,\nnbinary VARBINARY(10) NOT NULL,\nntiny_blob TINYBLOB NOT NULL,\nntiny_text_field TINYTEXT NOT NULL,\nempty_text TEXT NOT NULL,\nntext TEXT(10) NOT NULL,\nnmedium_blob MEDIUMBLOB NOT NULL,\nnmedium_text MEDIUMTEXT NOT NULL,\nnlong_blob LONGBLOB NOT NULL,\nnenum ENUM('test', 'test_one'),\nnset SET('test', 'test_one')\n)"))
