import math

import MySQLdb.cursors

from config import DATABASE
from dragonfly.exceptions import MissingClause, MissingTable, InvalidOperator, ChunkOutOfRange


class DB:
    """An easy way to interact with the configured database."""

    comparison_operators = ['=', '<=>', '<>', '!=', '>', '>=', '<', '<=', 'IN()', 'NOT', 'BETWEEN', 'IS NULL',
                            'IS NOT NULL', 'LIKE', 'EXISTS']

    def __init__(self, database_settings=DATABASE):
        """
        :param database_settings: The config for the database
        :type database_settings: dict
        """
        self.__database_settings = database_settings
        self.last_insert_id = None

        self.__query = {
            'select': 'SELECT *',
            'where': '',
            'table': ''
        }

        self.__query_params = {
            'where': []
        }

        self.__generated_params = None
        self.__generated_query = None

    def table(self, table_name):
        """The table that the query should be run on. This method must be run for any query to be executed."""
        self.__query['table'] = table_name
        return self

    def select(self, *args):
        """
        Equivalent to the ``SELECT`` command in MySQL.

        Pass all the columns you want to select to the function as normal arguments.

        :example:
            ``DB().select('title', 'text')``

        .. note:: If you would like to select all (``*``) columns then simply do not use the select argument when
        building your query.
        """
        self.__query['select'] = f"SELECT "

        for arg in args:
            self.__query['select'] += f"{arg}, "

        self.__query['select'] = self.__query['select'][:-2]

        return self

    def where(self, condition_1, comparison_operator, condition_2):
        """
        Equivalent to the ``WHERE`` command in SQL.

        :param condition_1: The value to the left of the operator.

        :param comparison_operator: The comparison operator, e.g ``=``
        :type comparison_operator: str

        :param condition_2: The value to the right of the operator.
        """
        if comparison_operator not in self.comparison_operators:
            raise InvalidOperator(f"Invalid comparison operator {comparison_operator} used")

        self.__query['where'] = f"WHERE {condition_1} {comparison_operator} %s"
        self.__query_params['where'] = [condition_2]

        return self

    def multiple_where(self, where_dict):
        """
        Allows for multiple where clauses through one command. Note this only supports the ``=`` operator.

        :param where_dict: The values to match
        :type where_dict: dict
        """
        to_append = ''

        for key, value in where_dict.items():
            to_append += f"{key} = %s AND "

        self.__query['where'] = f"WHERE {to_append[:-4]}"
        self.__query_params['where'] = list(where_dict.values())

        return self

    # Terminal methods
    def get(self):
        """This will execute the developer defined query and return all results."""
        self.__validate(['select'])

        self.__generated_query = f"{self.__query['select']} FROM {self.__query['table']} {self.__query['where']}"
        self.__generated_params = self.__query_params['where']

        return self.__execute_sql()

    def first(self):
        """This will execute the developer defined query and return only the first result (uses ``LIMIT 1``)"""
        self.__validate(['select'])

        self.__generated_query = f"{self.__query['select']} FROM {self.__query['table']} {self.__query['where']}"
        self.__generated_params = self.__query_params['where']

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

        original = f"{self.__query['select']} FROM `{self.__query['table']}`"

        where = self.__query['where']
        where_params = self.__query_params['where']

        self.__generated_query = f"SELECT COUNT(*) FROM {self.__query['table']}"
        rows = self.__execute_sql()[0]['COUNT(*)']

        if rows == 0:
            return None, None

        self.__generated_query = f"SELECT id FROM {self.__query['table']} ORDER BY id ASC LIMIT 1"
        lowest_id = self.__execute_sql()[0]['id']

        chunks = math.ceil(rows / chunk_size)

        if chunks < chunk_loc:
            raise ChunkOutOfRange(
                f"Chunk location of {chunk_loc} is greater than the number of chunks possible ({chunks})")

        max_id = (chunk_size * chunk_loc) + lowest_id
        min_id = (max_id - (chunk_size - 1)) - 1

        if bool(where):
            self.__generated_query = f"{original} {where} AND "
        else:
            self.__generated_query = f"{original} WHERE "

        self.__generated_query += f"id >= {min_id} AND id <= {max_id} LIMIT {chunk_size}"
        self.__generated_params = where_params

        meta = {'total': rows, 'per_page': chunk_size, 'current_page': chunk_loc, 'last_page': chunks, 'from': min_id,
                'to': max_id - 1}
        return self.__execute_sql(), meta

    def update(self, update_dict):
        """
        Updates the given row/rows based on the dictionary.

        For this method to run the :meth:`where<dragonfly.db.database.DB.where>` method must have been called before this one.

        :param update_dict: The dictionary containing the column to update and the value to update it with.
        :type update_dict: dict

        """

        self.__validate(['where'])

        self.__generated_query = f"UPDATE `{self.__query['table']}` SET "

        for key, value in update_dict.items():
            self.__generated_query += f"{key} = %s, "

        self.__generated_query = f"{self.__generated_query[:-2]} {self.__query['where']}"
        self.__generated_params = list(update_dict.values()) + self.__query_params['where']

        return self.__execute_sql()

    def delete(self):
        """
        Deletes the given row/rows baed on the developer defined query.

        For this method to run the :meth:`where<dragonfly.db.database.DB.where>` method must have been called first.

        """

        self.__validate(['where'])

        self.__generated_query = f"DELETE FROM `{self.__query['table']}` {self.__query['where']}"
        self.__generated_params = self.__query_params['where']

        return self.__execute_sql()

    def insert(self, insert_dict):
        """
        Inserts the given values into the database.

        :param insert_dict: The dictionary containing the column and the value to insert into the specified table
        :type insert_dict: dict

        """
        keys = ''
        values = ''

        for key in insert_dict.keys():
            keys += f"{key}, "
            values += '%s, '

        self.__generated_query = f"INSERT INTO `{self.__query['table']}` ({keys[:-2]}) VALUES ({values[:-2]})"
        self.__generated_params = list(insert_dict.values())

        return self.__execute_sql()

    def custom_sql(self, sql, n_rows=None):
        """
        Execute the custom SQL passed to the function.

        :param sql: The SQL code to execute
        :type sql: str

        :param n_rows: The number of rows to retrieve. If set to `None` returns all rows
        :type n_rows: int

        :return: The result of the SQL executed
        :rtype: dict

        """

        db = MySQLdb.connect(**self.__database_settings, cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db.cursor()

        cursor.execute(sql)
        db.commit()

        if n_rows is None:
            results = cursor.fetchall()
        elif n_rows == 1:
            results = cursor.fetchone()
        else:
            results = cursor.fetchmany(n_rows)

        cursor.close()
        db.close()

        return results

    def __execute_sql(self, n_rows=None):
        """
        Execute the user defined SQL.

        :param n_rows: The number of rows to retrieve. If set to `None` returns all rows
        :type: int

        :return: The result of the SQL executed
        :rtype: dict
        """

        db = MySQLdb.connect(**self.__database_settings, cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db.cursor()
        cursor.execute(self.__generated_query, self.__generated_params)

        db.commit()

        if n_rows is None:
            results = cursor.fetchall()
        elif n_rows == 1:
            results = cursor.fetchone()
        else:
            results = cursor.fetchmany(n_rows)

        cursor.execute("SELECT LAST_INSERT_ID()")

        # Store the last inserted id and query. This is used in the model class.
        self.last_insert_id = cursor.fetchone()['LAST_INSERT_ID()']
        self.last_query = cursor._last_executed

        cursor.close()
        db.close()

        self.__query = {
            'table': self.__query['table'],
            'select': 'SELECT *',
            'where': ''
        }

        self.__query_params = {
            'where': []
        }

        self.__generated_params = None
        self.__generated_query = None

        return results

    def __validate(self, required_parameters):
        """
        Validates whether the given SQL parameters are filled.

        :param required_parameters: The list of parameters that need to be checked
        :type: list
        """
        if self.__query['table'] == '':
            raise MissingTable('A valid table must be defined/chosen')

        required_dict = {k: v for k, v in self.__query.items() if k in required_parameters}

        if any(value == '' for value in required_dict.values()):
            raise MissingClause(f"Missing required SQL clause ({', '.join(required_parameters)})")
