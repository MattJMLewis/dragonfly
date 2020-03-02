import abc
import importlib

from dragonfly.db.database import DB


class Relationship(abc.ABC):
    """An abstract class that defines the interface each `Relationship` class should have"""

    def __init__(self, target, this_key=None, target_key=None):
        super().__init__()

        # Name of __target model
        self.target_name = target

        self._this_key = this_key
        self._target_key = target_key

        self._values = None
        self._target = None

    @abc.abstractmethod
    def delayed_init(cls, values, meta):
        """
        This function is executed when data needs to be retrieved.

        :param values: The database values of the given model
        :type values: dict

        :param meta: The meta values of the model
        :type meta: dict

        :return: The relationship class
        :rtype: :class:`Relationship <dragonfly.db.models.relationships.Relationship>`
        """


class HasMany(Relationship):
    """
    Retrieves all rows that have a have-many relationship with the model this class is initialised in.
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.index = 0

    def delayed_init(self, values, meta):

        self.index = 0

        # Get the target model class
        self.__target = getattr(importlib.import_module(f"models.{self.target_name}"), self.target_name.capitalize())()

        # If no target key (foreign key) has been given, generate from table name
        if self._target_key is None:
            self._target_key = meta['table_name'][:-1] + '_id'

        # If no primary key for this table has been given, generate from table name.
        if self._this_key is None:
            self._this_key = meta['primary_key'][0]

        self._values = self.__target.where(self._target_key, '=', values[self._this_key]).get()

        return self

    def __iter__(self):
        return self

    def __next__(self):
        # Enables class to be iterated over like list
        try:
            result = self._values[self.index]
        except IndexError:
            raise StopIteration

        self.index += 1

        return result

    def __getitem__(self, index):
        return self._values[index]

    def __len__(self):
        return len(self._values)

    def __bool__(self):
        # Returns False if no values retrieved
        return len(self._values) != 0


class BelongsTo(Relationship):
    """Retrieves the class that 'owns' the model this relationship is defined in."""

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def delayed_init(self, values, meta):

        self.__target = getattr(importlib.import_module(f"models.{self.target_name}"), self.target_name.capitalize())(
        )

        # The primary key of this target model
        if self._target_key is None:
            self._target_key = self.__target.primary_key[0]

        # The foreign key on the model relationship defined in
        if self._this_key is None:
            self._this_key = self.__target.meta['table_name'][:-1] + '_id'

        self._values = self.__target.where(self._target_key, '=', values[self._this_key]).first()

        return self._values

    def __bool__(self):
        return len(self._values) != 0

    def __repr__(self):
        return self._values


class ManyToMany(Relationship):

    def __init__(self, table=None, **kwargs):
        super().__init__(**kwargs)

        self.__table = table
        self.__index = 0

    def delayed_init(self, values, meta):

        self.__index = 0

        # Store target model before it is initialised
        self.__target_pre_init = self.__target = getattr(importlib.import_module(f"models.{self.target_name}"),
                                                     self.target_name.capitalize())
        self.__target = self.__target_pre_init()

        target_table = self.__target.meta['table_name']
        target_pk = self.__target.primary_key[0]

        # Generate keys if not passed in by user
        if self._target_key is None:
            self._target_key = target_table[:-1] + '_id'

        if self._this_key is None:
            self._this_key = meta['table_name'][:-1] + '_id'

        # Generate name of pivot table
        if self.__table is None:
            table_names = [meta['table_name'], target_table]
            self.__table = "_".join(sorted(table_names))

        # List of all columns in the target model table.
        columns = [f"{target_table}.{column}" for column in self.__target.fields_keys]

        # Select all the columns in the target model table where the primary key is equal to one of the keys in the
        # pivot table where the other key is equal to the id of this model.
        res = DB().custom_sql(
            f"SELECT {', '.join(columns)} FROM {target_table} INNER JOIN {self.__table} ON {target_table}.{target_pk} "
            f"= {self.__table}.{self._target_key} WHERE {self.__table}.{self._this_key} = {values[meta['primary_key'][0]]}")

        self.values = [self.__target_pre_init(data=row) for row in res]

        return self

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self._values[self.__index]
        except IndexError:
            raise StopIteration

        self.__index += 1

        return result

    def __getitem__(self, index):
        return self._values[index]

    def __len__(self):
        return len(self._values)

    def __bool__(self):
        return len(self._values) != 0
