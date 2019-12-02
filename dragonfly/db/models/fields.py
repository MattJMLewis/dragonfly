import abc

from dragonfly.db.table import Table


class ForeignKey:

    def __init__(self, *args):
        self.local_keys = args

    def references(self, *args):
        self.foreign_keys = args
        return self

    def on(self, table):
        self.table = table
        return self


class Unique:
    def __init__(self, *args):
        self.args = args


class PrimaryKey:
    def __init__(self, *args):
        self.args = args


class Field(abc.ABC):
    """An abstract class that defines the interface each `Field` class should have."""

    def __init__(self, name=None, null=False, blank=False, default=None, unique=False, primary_key=False):
        super().__init__()
        self.name = name
        self.blank = blank

        self.default_parameters = {
            'null': null,
            'default': default,
            'unique': unique,
            'primary_key': primary_key
        }

        if default is None:
            del self.default_parameters['default']

    @abc.abstractmethod
    def to_python_type(cls, value):
        """
        This is how the value from the database should be converted to python. Note that at the moment this is not
        currently in use as the MySQL adapter does this automatically
        """
        pass

    @abc.abstractmethod
    def to_database_type(cls):
        """
        This instructs the database migrator on how to generate the SQL for the model.
        """
        pass


# Numeric types

class BitField(Field):

    def __init__(self, length=None, **kwargs):
        super().__init__(**kwargs)

        self.length = length

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.bit(self.length, **self.default_parameters)


class BoolField(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return bool(value)

    def to_database_type(self):
        return Table.boolean(**self.default_parameters)


class IntField(Field):

    def __init__(self, length=None, unsigned=False, auto_increment=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.integer_parameters = {
            'unsigned': unsigned,
            'auto_increment': auto_increment,
            'zerofill': zerofill
        }

        self.length = length

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.integer(self.length, **self.integer_parameters, **self.default_parameters)


class BigIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.bigint(self.length, **self.integer_parameters, **self.default_parameters)


class MediumIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.mediumint(self.length, **self.integer_parameters, **self.default_parameters)


class SmallIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.smallint(self.length, **self.integer_parameters, **self.default_parameters)


class TinyIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.tinyint(self.length, **self.integer_parameters, **self.default_parameters)


class DecimalField(Field):

    def __init__(self, digits=None, decimal_places=None, unsigned=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.decimal_parameters = {
            'unsigned': unsigned,
            'zerofill': zerofill
        }

        self.digits = digits
        self.decimal_places = decimal_places

    def to_python_type(self, value):
        return float(value)

    def to_database_type(self):
        return Table.decimal(self.digits, self.decimal_places, **self.decimal_parameters, **self.default_parameters)


class DoubleField(Field):

    def __init__(self, digits=None, decimal_places=None, unsigned=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.decimal_parameters = {
            'unsigned': unsigned,
            'zerofill': zerofill
        }

        self.digits = digits
        self.decimal_places = decimal_places

    def to_python_type(self, value):
        return float(value)

    def to_database_type(self):
        return Table.double(self.digits, self.decimal_places, **self.decimal_parameters, **self.default_parameters)


class FloatField(Field):

    def __init__(self, digits=None, unsigned=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.decimal_parameters = {
            'unsigned': unsigned,
            'zerofill': zerofill
        }

        self.digits = digits

    def to_python_type(self, value):
        return float(value)

    def to_database_type(self):
        return Table.float(self.digits, **self.decimal_parameters, **self.default_parameters)


# Date and time types


class DateField(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.date(**self.default_parameters)


class DateTimeField(Field):

    def __init__(self, fsp=None, **kwargs):
        super().__init__(**kwargs)

        self.fsp = fsp

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.datetime(self.fsp, **self.default_parameters)


class TimestampField(Field):

    def __init__(self, fsp=None, on=None, **kwargs):
        super().__init__(**kwargs)

        self.fsp = fsp
        self.on = on

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.timestamp(self.fsp, self.on, **self.default_parameters)


class TimeField(Field):

    def __init__(self, fsp=None, **kwargs):
        super().__init__(**kwargs)

        self.fsp = fsp

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.time(self.fsp, **self.default_parameters)


class YearField(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.year(**self.default_parameters)

# String types


class CharField(Field):

    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)

        self.max_length = max_length

    def to_python_type(self, value):
        return str(value)

    def to_database_type(self):
        return Table.char(self.max_length, **self.default_parameters)


class TextField(Field):

    def __init__(self, length=None, **kwargs):
        super().__init__(**kwargs)
        self.length = length

    def to_python_type(self, value):
        return str(value)

    def to_database_type(self):
        return Table.text(self.length, **self.default_parameters)
