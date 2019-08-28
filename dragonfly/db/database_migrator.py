import importlib
from config import ROOT_DIR
import os
import glob
from dragonfly.db.models.fields import ForeignKey, Unique, PrimaryKey
from dragonfly.db.table import Table


class DatabaseMigrator:
    """Generates the SQL to create a table that corresponds to the defined model/s"""

    def __init__(self, path='models'):
        """
        Generates the SQL to create a table that corresponds to the defined model/s. This SQL is stored in the `.tables`
        dictionary.

        :param path: The location of the models to migrate
        :type path: str
        """
        self.path = path
        self.models = [os.path.basename(x)[:-3] for x in glob.glob(f"{ROOT_DIR}/models/*.py")]
        self.tables = {}

        for model in self.models:
            cls = getattr(importlib.import_module(f"models.{model}"), model.capitalize())()
            self.tables[cls.meta['table_name']] = self.__generate_sql(cls)

    @staticmethod
    def __generate_sql(model):
        """Generate the SQL for the given model."""

        sql = f"CREATE TABLE {model.meta['table_name']} (\n"

        for key, value in model.types.items():
            sql += f"{key} {value.to_database_type()},\n"

        for key, value in model.meta.items():

            if key == 'table_name':
                break

            if isinstance(value, ForeignKey):
                to_append = Table.foreign_key(key, value.table, value.local_keys, value.foreign_keys)

            if isinstance(value, Unique):
                to_append = Table.unique(*value.args, constraint_name=key)

            if isinstance(value, PrimaryKey):
                to_append = Table.primary_key(*value.args)

            sql += f"{to_append}, \n"

        sql = sql.rstrip()
        sql = sql[:-1]
        sql += "\n)"

        return sql
