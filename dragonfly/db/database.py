import MySQLdb.cursors
import math

from config import DATABASE


class DB:
    """An easy way to interact with the configured database."""

    def __init__(self, database_settings=DATABASE):
        """
        :param database_settings: The config for the database
        :type database_settings: dict
        """
        self.query = {
            'table': '',
            'where': '',
            'select': 'SELECT *'
        }
        self.database = database_settings
        self.raw_query = ''

        self.last_insert_id = None

    # Required method
    def table(self, table_name):
        """The table that the query should be run on. This method must be run for any query to be executed."""
        self.query['table'] = table_name
        return self

    def where(self, condition_1, operator, condition_2):
        """
        Equivalent to the ``WHERE`` clause in SQL.

        :param condition_1: The value to the left of the operator.

        :param operator: The operator, e.g ``=``
        :type operator: str

        :param condition_2: The value to the right of the operator.
        """

        self.query['where'] = f"WHERE {condition_1} {operator} {to_mysql_type(condition_2)}"
        return self

    def multiple_where(self, where_dict):
        """
        Allows for multiple where clauses through one command. Note this only supports the ``=`` operator.

        :param where_dict: Each key, value pair in the dictionary becomes ``WHERE key = value``.
        :type where_dict: dict
        """

        self.query['where'] = f"WHERE "

        for key, value in where_dict.items():
            self.query['where'] += f"{key} = {to_mysql_type(value)} AND "

        self.query['where'] = self.query['where'][:-4]

        return self

    def select(self, *args):
        """
        Equivalent to the ``SELECT`` clause in MySQL.

        Add the column you would like as an argument to the function. You can choose many columns.

        :example:
            ``DB().select('title', 'text')``

        .. note:: If you would like to select all (``*``) columns then simply do not use the select argument when
        building your query.
        """
        columns = ','.join(f" `{column}`" for column in args)
        self.query['select'] = f"SELECT {columns}"
        return self

    # Terminal methods
    def get(self):
        """This will execute the query you have been building and return all results."""
        self.__validate(['select'])
        self.raw_query = f"{self.query['select']} FROM `{self.query['table']}` {self.query['where']}"

        return self.__execute_sql()

    def first(self):
        """This will execute the query you have been building and return only the first result (uses ``LIMIT 1``)"""
        self.__validate(['select'])
        self.raw_query = f"{self.query['select']} FROM `{self.query['table']}` {self.query['where']} LIMIT 1"

        return self.__execute_sql(1)

    def chunk(self, chunk_loc, chunk_size):
        """
        This will run the given query and return the given number of results at the given location.

        :param chunk_loc: The location to chunk e.g the first chunk or second chunk.
        :type chunk_loc: int

        :param chunk_size: The number of rows each chunk should contain.
        :type chunk_size: int

        """
        self.__validate(['select'])

        original = f"{self.query['select']} FROM `{self.query['table']}` {self.query['where']}"
        is_where = bool(self.query['where'])

        self.raw_query = f"SELECT COUNT(*) FROM {self.query['table']}"
        rows = self.__execute_sql()[0]['COUNT(*)']

        chunks = math.ceil(rows / chunk_size)

        if chunks < chunk_loc:
            raise Exception("Chunk loc out of range")

        max_id = chunk_size * chunk_loc
        min_id = max_id - (chunk_size - 1)

        if is_where:
            self.raw_query = f"{original}AND "
        else:
            self.raw_query = f"{original}WHERE "

        self.raw_query += f"id >= {min_id} AND id <= {max_id} LIMIT {chunk_size}"

        return self.__execute_sql()

    def update(self, update_dict):
        """
        Updates the given row/rows based on the dictionary.

        For this method to run the :meth:`where<dragonfly.db.database.DB.where>` method must have been called before this one.

        :param update_dict: The dictionary containing the column to update and the value to update it with.
        :type update_dict: dict

        """

        self.__validate(['where'])

        dictionary_string = ''
        for key, value in update_dict.items():
            dictionary_string += f"{key} = {to_mysql_type(value)}, "

        self.raw_query = f"UPDATE `{self.query['table']}` SET {dictionary_string[:-2]} {self.query['where']}"

        return self.__execute_sql()

    def delete(self):
        """
        Deletes the given row/rows.

        For this method to run the :meth:`where<dragonfly.db.database.DB.where>` method must have been called before this one.

        """

        self.__validate(['where'])
        self.raw_query = f"DELETE FROM `{self.query['table']}` {self.query['where']}"

        return self.__execute_sql()

    def insert(self, insert_dict):
        """
        Inserts the given values into the database.

        :param insert_dict: The dictionary containing the column and the value to insert into that column
        :type insert_dict: dict

        """

        value_str = ''
        for value in insert_dict.values():
            value_str += f"{to_mysql_type(value)}, "

        self.raw_query = f"INSERT INTO `{self.query['table']}` ({', '.join(insert_dict.keys())}) VALUES ({value_str[:-2]})"

        return self.__execute_sql()

    def __execute_sql(self, n_rows=None):
        """Executes the SQL that the user built"""

        db = MySQLdb.connect(**self.database, cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db.cursor()
        cursor.execute(self.raw_query)
        db.commit()

        if n_rows is None:
            results = cursor.fetchall()
        elif n_rows == 1:
            results = cursor.fetchone()
        else:
            results = cursor.fetchmany(n_rows)

        cursor.execute("SELECT LAST_INSERT_ID()")
        self.last_insert_id = cursor.fetchone()['LAST_INSERT_ID()']

        cursor.close()
        db.close()

        self.query = {
            'table': self.query['table'],
            'where': '',
            'select': 'SELECT *'
        }

        self.raw_query = ''

        return results

    def __validate(self, required_parameters):
        """Validates that the given parameter has been filled."""
        if self.query['table'] == '':
            raise Exception('Table must be defined')

        required_dict = {k: v for k, v in self.query.items() if k in required_parameters}

        if any(value == '' for value in required_dict.values()):
            raise Exception(f"Missing required parameter ({', '.join(required_parameters)})")


def to_mysql_type(value):
    if isinstance(value, str):
        return f"'{value}'"

    return value
