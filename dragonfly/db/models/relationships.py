import abc
from dragonfly.db.database import DB
import importlib


class Relationship(abc.ABC):
    """An abstract class that defines the interface each `Relationship` class should have"""

    def __init__(self, target, this_key=None, target_key=None):
        super().__init__()

        self.target_name = target
        self.this_key = this_key
        self.target_key = target_key

        self.values = None
        self.target = None

    @abc.abstractmethod
    def delayed_init(cls, values, meta):
        """
        How the relationship should retrieve the given data.
        """
        pass


class HasMany(Relationship):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.index = 0

    def delayed_init(self, values, meta):

        self.index = 0

        self.target = getattr(importlib.import_module(f"models.{self.target_name}"), self.target_name.capitalize())()

        if self.target_key is None:
            self.target_key = meta['table_name'][:-1] + '_id'

        if self.this_key is None:
            self.this_key = meta['primary_key'][0]

        self.values = self.target.where(self.target_key, '=', values[self.this_key]).get()

        return self

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.values[self.index]
        except IndexError:
            raise StopIteration

        self.index += 1

        return result

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return len(self.values)

    def __bool__(self):
        return len(self.values) != 0


class BelongsTo(Relationship):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def delayed_init(self, values, meta):

        self.target = getattr(importlib.import_module(f"models.{self.target_name}"), self.target_name.capitalize())(
        )

        if self.target_key is None:
            self.target_key = self.target.primary_key[0]

        if self.this_key is None:
            self.this_key = self.target.meta['table_name'][:-1] + '_id'

        self.values = self.target.where(self.target_key, '=', values[self.this_key]).first()

        return self.values

    def __bool__(self):
        return len(self.values) != 0

    def __repr__(self):
        return self.values


class ManyToMany(Relationship):

    def __init__(self, table=None, **kwargs):
        super().__init__(**kwargs)

        self.table = table
        self.index = 0

    def delayed_init(self, values, meta):

        self.index = 0

        self.target_pre_init = self.target = getattr(importlib.import_module(f"models.{self.target_name}"),
                                                     self.target_name.capitalize())
        self.target = self.target_pre_init()

        target_table = self.target.meta['table_name']
        target_pk = self.target.primary_key[0]

        if self.target_key is None:
            self.target_key = target_table[:-1] + '_id'

        if self.this_key is None:
            self.this_key = meta['table_name'][:-1] + '_id'

        if self.table is None:
            table_names = [meta['table_name'], target_table]
            self.table = "_".join(sorted(table_names))

        columns = [f"{target_table}.{column}" for column in self.target.types_keys]

        res = DB().custom_sql(
            f"SELECT {', '.join(columns)} FROM {target_table} INNER JOIN {self.table} ON {target_table}.{target_pk} "
            f"= {self.table}.{self.target_key} WHERE {self.table}.{self.this_key} = {values[meta['primary_key'][0]]}")

        self.values = [self.target_pre_init(data=row) for row in res]

        return self

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.values[self.index]
        except IndexError:
            raise StopIteration

        self.index += 1

        return result

    def __getitem__(self, index):
        return self.values[index]

    def __len__(self):
        return len(self.values)

    def __bool__(self):
        return len(self.values) != 0
