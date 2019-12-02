import MySQLdb.cursors
import math

from config import DATABASE


class DB:
    """An easy way to interact with the configured database."""

    comparison_operators = ['=', '<=>', '<>', '!=', '>', '>=', '<', '<=', 'IN()', 'NOT', 'BETWEEN', 'IS NULL',
                            'IS NOT NULL', 'LIKE', 'EXISTS']

    def __init__(self, database_settings=DATABASE):
        """
        :param database_settings: The config for the database
        :type database_settings: dict
        """
        self.database_settings = database_settings
        self.last_insert_id = None

        self.query = {
            'select': 'SELECT *',
            'where': ''
        }

        self.query_params = {
            'where': []
        }

        self.generated_params = None
        self.generated_query = None

    def table(self, table_name):
        """The table that the query should be run on. This method must be run for any query to be executed."""
        self.query['table'] = table_name
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
        self.query['select'] = f"SELECT "

        for arg in args:
            self.query['select'] += f"{arg}, "

        self.query['select'] = self.query['select'][:-2]

        return self

    def where(self, condition_1, comparison_operator, condition_2):
        """
        Equivalent to the ``WHERE`` clause in SQL.

        :param condition_1: The value to the left of the operator.

        :param comparison_operator: The operator, e.g ``=``
        :type comparison_operator: str

        :param condition_2: The value to the right of the operator.
        """
        if comparison_operator not in self.comparison_operators:
            raise Exception("Invalid comparison operator.")

        self.query['where'] = f"WHERE {condition_1} {comparison_operator} %s"
        self.query_params['where'] = [condition_2]

        return self
    
    def multiple_where(self, where_dict):
        """
        Allows for multiple where clauses through one command. Note this only supports the = operator.

        :param where_dict: The values to match
        :type where_dict: dict
        """
        to_append = ''

        for key, value in where_dict.items():
            to_append += f"{key} = %s AND "

        self.query['where'] = f"WHERE {to_append[:-4]}"
        self.query_params['where'] = list(where_dict.values())

        return self

    # Terminal methods
    def get(self):
        """This will execute the query you have been building and return all results."""
        self.__validate(['select'])

        self.generated_query = f"{self.query['select']} FROM {self.query['table']} {self.query['where']}"
        self.generated_params = self.query_params['where']

        return self.__execute_sql()

    def first(self):
        """This will execute the query you have been building and return only the first result (uses ``LIMIT 1``)"""
        self.__validate(['select'])

        self.generated_query = f"{self.query['select']} FROM {self.query['table']} {self.query['where']}"
        self.generated_params = self.query_params['where']

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

        original = f"{self.query['select']} FROM `{self.query['table']}`"

        where = self.query['where']
        where_params = self.query_params['where']

        self.generated_query = f"SELECT COUNT(*) FROM {self.query['table']}"
        rows = self.__execute_sql()[0]['COUNT(*)']

        chunks = math.ceil(rows / chunk_size)

        if chunks < chunk_loc:
            raise Exception("Chunk loc out of range")

        max_id = chunk_size * chunk_loc
        min_id = max_id - (chunk_size - 1)

        if bool(where):
            self.generated_query = f"{original} {where} AND "
        else:
            self.generated_query = f"{original} WHERE "

        self.generated_query += f"id >= {min_id} AND id <= {max_id} LIMIT {chunk_size}"
        self.generated_params = where_params

        return self.__execute_sql()

    def update(self, update_dict):
        """
        Updates the given row/rows based on the dictionary.

        For this method to run the :meth:`where<dragonfly.db.database.DB.where>` method must have been called before this one.

        :param update_dict: The dictionary containing the column to update and the value to update it with.
        :type update_dict: dict

        """

        self.__validate(['where'])

        self.generated_query = f"UPDATE `{self.query['table']}` SET "

        for key, value in update_dict.items():
            self.generated_query += f"{key} = %s, "

        self.generated_query = f"{self.generated_query[:-2]} {self.query['where']}"
        self.generated_params = list(update_dict.values()) + self.query_params['where']

        return self.__execute_sql()

    def delete(self):
        """
        Deletes the given row/rows.

        For this method to run the :meth:`where<dragonfly.db.database.DB.where>` method must have been called before this one.

        """

        self.__validate(['where'])

        self.generated_query = f"DELETE FROM `{self.query['table']}` {self.query['where']}"
        self.generated_params = self.query_params['where']

        return self.__execute_sql()

    def insert(self, insert_dict):
        """
        Inserts the given values into the database.

        :param insert_dict: The dictionary containing the column and the value to insert into that column
        :type insert_dict: dict

        """
        keys = ''
        values = ''

        for key in insert_dict.keys():
            keys += f"{key}, "
            values += '%s, '

        self.generated_query = f"INSERT INTO `{self.query['table']}` ({keys[:-2]}) VALUES ({values[:-2]})"
        self.generated_params = list(insert_dict.values())

        return self.__execute_sql()

    def custom_sql(self, sql, n_rows=None):

        db = MySQLdb.connect(**self.database_settings, cursorclass=MySQLdb.cursors.DictCursor)
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
        """Executes the SQL that the user built"""

        db = MySQLdb.connect(**self.database_settings, cursorclass=MySQLdb.cursors.DictCursor)
        cursor = db.cursor()
        cursor.execute(self.generated_query, self.generated_params)

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
            'select': 'SELECT *',
            'where': ''
        }

        self.query_params = {
            'where': []
        }

        self.generated_params = None
        self.generated_query = None

        return results

    def __validate(self, required_parameters):
        """Validates that the given parameter has been filled."""
        if self.query['table'] == '':
            raise Exception('Table must be defined')

        required_dict = {k: v for k, v in self.query.items() if k in required_parameters}

        if any(value == '' for value in required_dict.values()):
            raise Exception(f"Missing required parameter ({', '.join(required_parameters)})")
