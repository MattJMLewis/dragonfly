import abc

from dragonfly.db.table import Table


class ForeignKey:
    """
    Provides a way to define foreign key relationships in a model.

    Should be called in the following order:
        ForeignKey('local_key').refrences('foreign_key').on('table')

    """

    def __init__(self, *args):
        """
        Defines the list of local keys that reference a field on another table.

        :param args: A list of local keys that reference a field on another table.
        """
        self.local_keys = args

    def references(self, *args):
        """
        Defines the foreign keys that the local keys reference.

        :param args: A list of foreign keys that the defined local keys reference.

        :return: This ForeignKey object.
        :rtype: :class:`ForeignKey <dragonfly.db.models.fields.ForeignKey>`
        """
        self.foreign_keys = args
        return self

    def on(self, table):
        """
        The table the foreign keys are on.

        :param table: The table that the foreign keys are located on

        :return: This ForeignKey object.
        :rtype: :class:`ForeignKey <dragonfly.db.models.fields.ForeignKey>`
        """
        self.table = table

        return self


class Unique:
    """Provides a way to make a field a model unique """

    def __init__(self, *args):
        """
        :param args: The fields to make unique
        """
        self.fields = args


class PrimaryKey:
    """Provides a way to make the given field(s) a primary key """

    def __init__(self, *args):
        """
        Sets the given fields as primary keys.

        :param args: The fields to set as a primary key
        """
        self.fields = args


class Field(abc.ABC):
    """An abstract class that defines the interface each ``Field`` class should have."""

    def __init__(self, name=None, null=False, blank=False, default=None, unique=False, primary_key=False):
        """

        :param name: The name of the field
        :type: str

        :param null: If the field should be nullable
        :type: bool

        :param blank: If the field can be _blank
        :type: bool

        :param default: The default value of the field (if any)
        :type: str

        :param unique: If the field should be unique
        :type: bool

        :param primary_key: If the field is a primary key
        :type: bool

        """

        super().__init__()
        self._name = name
        self._blank = blank

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
        currently in use as the MySQLdb package does this automatically.

        :param value: The value to convert
        """
        pass

    @abc.abstractmethod
    def to_database_type(cls):
        """This instructs the database migrator on how to generate the SQL for the field."""
        pass


# Numeric types

class BitField(Field):

    def __init__(self, length=None, **kwargs):
        super().__init__(**kwargs)

        self.__length = length

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.bit(self.__length, **self.default_parameters)


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

        self._length = length

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.integer(self._length, **self.integer_parameters, **self.default_parameters)


class BigIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.bigint(self._length, **self.integer_parameters, **self.default_parameters)


class MediumIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return int(value)

    def to_database_type(self):
        return Table.mediumint(self._length, **self.integer_parameters, **self.default_parameters)


class SmallIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.smallint(self._length, **self.integer_parameters, **self.default_parameters)


class TinyIntField(IntField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.tinyint(self._length, **self.integer_parameters, **self.default_parameters)


class DecimalField(Field):

    def __init__(self, digits=None, decimal_places=None, unsigned=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.decimal_parameters = {
            'unsigned': unsigned,
            'zerofill': zerofill
        }

        self.__digits = digits
        self.__decimal_places = decimal_places

    def to_python_type(self, value):
        return float(value)

    def to_database_type(self):
        return Table.decimal(self.__digits, self.__decimal_places, **self.decimal_parameters, **self.default_parameters)


class DoubleField(Field):

    def __init__(self, digits=None, decimal_places=None, unsigned=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.decimal_parameters = {
            'unsigned': unsigned,
            'zerofill': zerofill
        }

        self.__digits = digits
        self.__decimal_places = decimal_places

    def to_python_type(self, value):
        return float(value)

    def to_database_type(self):
        return Table.double(self.__digits, self.__decimal_places, **self.decimal_parameters, **self.default_parameters)


class FloatField(Field):

    def __init__(self, digits=None, unsigned=False, zerofill=False, **kwargs):
        super().__init__(**kwargs)

        self.decimal_parameters = {
            'unsigned': unsigned,
            'zerofill': zerofill
        }

        self.__digits = digits

    def to_python_type(self, value):
        return float(value)

    def to_database_type(self):
        return Table.float(self.__digits, **self.decimal_parameters, **self.default_parameters)


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

        self.__fsp = fsp

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.datetime(self.__fsp, **self.default_parameters)


class TimestampField(Field):

    def __init__(self, fsp=None, on=None, **kwargs):
        super().__init__(**kwargs)

        self.__fsp = fsp
        self.__on = on

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.timestamp(self.__fsp, self.__on, **self.default_parameters)


class TimeField(Field):

    def __init__(self, fsp=None, **kwargs):
        super().__init__(**kwargs)

        self.__fsp = fsp

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.time(self.__fsp, **self.default_parameters)


class YearField(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return value

    def to_database_type(self):
        return Table.year(**self.default_parameters)


# String types


class StringField(Field):

    def __init__(self, length=None, **kwargs):
        super().__init__(**kwargs)

        self._length = length

    def to_python_type(self, value):
        return str(value)

    def to_database_type(self):
        pass


class VarCharField(StringField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.varchar(self._length, **self.default_parameters)


class CharField(StringField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.char(self._length, **self.default_parameters)


class TextField(StringField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_database_type(self):
        return Table.text(self._length, **self.default_parameters)


class BinaryField(StringField):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return bool(value)

    def to_database_type(self):
        return Table.varbinary(self._length, **self.default_parameters)


class TinyBlobField(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return bytes(value)

    def to_database_type(self):
        return Table.tinyblob(**self.default_parameters)


class TinyTextField(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return str(value)

    def to_database_type(self):
        return Table.tinytext(**self.default_parameters)


class MediumBlob(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return bytes(value)

    def to_database_type(self):
        return Table.mediumblob(**self.default_parameters)


class MediumText(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return str(value)

    def to_database_type(self):
        return Table.mediumtext(**self.default_parameters)


class LongBlob(Field):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python_type(self, value):
        return bytes(value)

    def to_database_type(self):
        return Table.longblob(**self.default_parameters)


class Enum(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.enum = args

    def to_python_type(self, value):
        return list(value)

    def to_database_type(self):
        return Table.enum(*self.enum)


class Set(Field):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.__set = args

    def to_python_type(self, value):
        return list(value)

    def to_database_type(self):
        return Table.set(*self.__set)
