import glob
import importlib
import os

from config import ROOT_DIR
from dragonfly.db.models.fields import ForeignKey, Unique, PrimaryKey
from dragonfly.db.table import Table


class DatabaseMigrator:
    """Generates the SQL to create a table that corresponds to the defined model(s)"""

    def __init__(self, path='models'):
        """
        Generates the SQL to create a table that corresponds to the defined model(s). This SQL is stored in the ``.tables``
        dictionary.

        :param path: The location of the models to migrate
        :type path: str
        """
        self.path = path
        self.models = [os.path.basename(x)[:-3] for x in glob.glob(f"{ROOT_DIR}/{path}/*.py")]
        self.tables = {}

        import_path = path.replace('/', '.')
        for model in self.models:
            # Generate model name
            model_name = model.title().replace("_", "")
            cls = getattr(importlib.import_module(f"{import_path}.{model}"), model_name)()
            self.tables[cls.meta['table_name']] = self.__generate_sql(cls)

    @staticmethod
    def __generate_sql(model):
        """
        Generate the SQL for the given model.

        :param model: The model class
        :type :class:`Model <dragonfly.db.models.model.Model>`

        :return: The generated SQL
        """
        depends = []

        sql = f"CREATE TABLE {model.meta['table_name']} (\n"

        # Get all fields
        for key, value in model.fields.items():
            sql += f"{key} {value.to_database_type()},\n"

        # Get any meta information
        for key, value in model.meta.items():

            if isinstance(value, ForeignKey):
                to_append = Table.foreign_key(key, value.table, value.local_keys, value.foreign_keys)
                # If foreign key present this table must depend __on the existence of another
                depends.append(value.table)
                sql += f"{to_append}, \n"

            elif isinstance(value, Unique):
                to_append = Table.unique(*value.fields, constraint_name=key)
                sql += f"{to_append}, \n"

            elif isinstance(value, PrimaryKey):
                to_append = Table.primary_key(*value.fields)
                sql += f"{to_append}, \n"

        sql = sql.rstrip()
        sql = sql[:-1]
        sql += "\n)"

        return depends, sql
