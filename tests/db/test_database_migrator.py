from unittest import TestCase
from dragonfly.db.database_migrator import DatabaseMigrator


class TestDatabaseMigrator(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dbm = DatabaseMigrator(path='tests/models')

    def test_table_name(self):
        self.assertEqual(self.dbm.tables['different_name'], ([], 'CREATE TABLE different_name \n)'))

    def test_id(self):
        self.assertEqual(self.dbm.tables['ids'], ([], 'CREATE TABLE ids (\ncreated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\nupdated_at TIMESTAMP ON UPDATE NOW() DEFAULT NOW()\n)'))

    def test_timestamps(self):
        self.assertEqual(self.dbm.tables['timestamps'], ([], 'CREATE TABLE timestamps \n)'))

    def test_null(self):
        self.assertEqual(self.dbm.tables['nulls'], ([], 'CREATE TABLE nulls (\nstring CHAR NULL\n)'))

    def test_primary_key(self):
        self.assertEqual(self.dbm.tables['primarykeys'], ([], 'CREATE TABLE primarykeys (\nstring CHAR PRIMARY KEY,\nanother_string CHAR,\nPRIMARY KEY (another_string)\n)'))

    def test_unique(self):
        self.assertEqual(self.dbm.tables['uniques'], ([], 'CREATE TABLE uniques (\nstring CHAR UNIQUE\n)'))

    def test_default(self):
        self.assertEqual(self.dbm.tables['defaults'], ([], "CREATE TABLE defaults (\nstring CHAR DEFAULT 'testing',\nsecond_string CHAR DEFAULT 1\n)"))

    def test_all_fields(self):
        self.assertEqual(self.dbm.tables['fields'], ([], "CREATE TABLE fields (\nempty_bit BIT,\nnbit BIT(10),\nempty_tiny_int TINYINT,\nntiny_int TINYINT(10),\nnbool BOOLEAN,\nempty_small_int SMALLINT,\nnsmall_int SMALLINT(10),\nempty_medium_int MEDIUMINT,\nnmedium_int MEDIUMINT(10),\nempty_int INT,\nnint INT(10),\nempty_big_int BIGINT,\nnbig_int BIGINT(10),\nempty_decimal DECIMAL,\nndecimal DECIMAL(5, 2),\nempty_float FLOAT,\nnfloat FLOAT(10),\nempty_double DOUBLE,\nndouble DOUBLE(5, 2),\nndate DATE,\nempty_datetime DATETIME,\nndatetime DATETIME(6),\nempty_timestamp TIMESTAMP,\nntimestamp TIMESTAMP ON UPDATE CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\nnn_timestamp TIMESTAMP(6) NULL,\nempty_time TIME,\nntime TIME(6),\nnyear YEAR,\nempty_varchar VARCHAR(15),\nnvarchar VARCHAR(10),\nempty_char CHAR,\nnchar CHAR(255),\nempty_binary VARBINARY(15),\nnbinary VARBINARY(10),\nntiny_blob TINYBLOB,\nntiny_text_field TINYTEXT,\nempty_text TEXT,\nntext TEXT(10),\nnmedium_blob MEDIUMBLOB,\nnmedium_text MEDIUMTEXT,\nnlong_blob LONGBLOB,\nnenum ENUM('test', 'test_one'),\nnset SET('test', 'test_one')\n)"))
