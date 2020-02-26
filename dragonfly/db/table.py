from string import Template

# In format of option name: (SQL equivalent, is a template)
sql_to_var = \
    {
        # Numeric types only
        'unsigned': ('UNSIGNED', False),
        'zerofill': ('ZEROFILL', False),
        'auto_increment': ('AUTO_INCREMENT', False),

        # Defaults
        'null': ('NULL', False),
        'default': (Template('DEFAULT $parameter'), True),
        'unique': ('UNIQUE', False),
        'primary_key': ('PRIMARY KEY', False),

    }


def handle_options(func):
    """Handles any extra options for the methods on the :class:`Table` class"""
    def wrapper(*args, **kwargs):
        append = ''

        for key in list(kwargs):
            # If not a valid SQL option
            if key not in sql_to_var.keys():
                raise Exception("Invalid argument")

            key_tuple = sql_to_var[key]

            # If a template substitute the given value into the string
            if key_tuple[1]:
                append += ' ' + key_tuple[0].substitute(parameter=kwargs[key])
            else:
                # If key passed into function add the SQL to a string
                if kwargs[key]:
                    append += ' ' + key_tuple[0]
                if key == 'null':
                    # Null works in the opposite way to the other values. If null not true __set SQL to NOT NULL
                    if not kwargs[key]:
                        append += ' NOT NULL'

            # Delete the key from the kwargs so it does not interfere with the function to be executed.
            del kwargs[key]

        # Get the SQL result from the function and append the extra SQL generated
        return func(*args, **kwargs) + append

    return wrapper


class Table:
    """Returns the MySQL code to create a column in a table with the given type."""

    # Numeric types

    @staticmethod
    @handle_options
    def bit(length):
        if length:
            return f"BIT({length})"

        return "BIT"

    @staticmethod
    @handle_options
    def tinyint(length):
        if length:
            return f"TINYINT({length})"

        return "TINYINT"

    @staticmethod
    @handle_options
    def boolean():
        return f"BOOLEAN"

    @staticmethod
    @handle_options
    def smallint(length):
        if length:
            return f"SMALLINT({length})"

        return "SMALLINT"

    @staticmethod
    @handle_options
    def mediumint(length):
        if length:
            return f"MEDIUMINT({length})"

        return "MEDIUMINT"

    @staticmethod
    @handle_options
    def integer(length=None):
        if length:
            return f"INT({length})"

        return "INT"

    @staticmethod
    @handle_options
    def bigint(length):
        if length:
            return f"BIGINT({length})"

        return "BIGINT"

    @staticmethod
    @handle_options
    def decimal(digits, decimal_places):
        if digits is None and decimal_places is None:
            return "DECIMAL"

        return f"DECIMAL({digits}, {decimal_places})"

    @staticmethod
    @handle_options
    def float(length):
        if length:
            return f"FLOAT({length})"

        return f"FLOAT"

    @staticmethod
    @handle_options
    def double(digits, decimal_places):
        if digits is None and decimal_places is None:
            return "DOUBLE"

        return f"DOUBLE({digits}, {decimal_places})"

    # Date and time types

    @staticmethod
    @handle_options
    def date():
        return f"DATE"

    @staticmethod
    @handle_options
    def datetime(fsp):
        if fsp:
            return f"DATETIME({fsp})"

        return "DATETIME"

    @staticmethod
    @handle_options
    def timestamp(fsp, on):
        if on and fsp:
            return f"TIMESTAMP({fsp}) ON {on}"
        if fsp:
            return f"TIMESTAMP({fsp})"
        if on:
            return f"TIMESTAMP ON {on}"

        return "TIMESTAMP"

    @staticmethod
    @handle_options
    def time(fsp):
        if fsp:
            return f"TIME({fsp})"

        return "TIME"

    @staticmethod
    @handle_options
    def year():
        return f"YEAR"

    # String types

    @staticmethod
    @handle_options
    def char(size):
        if size:
            return f"CHAR({size})"

        return "CHAR"

    @staticmethod
    @handle_options
    def varchar(size):
        if size:
            return f"VARCHAR({size})"

        return "VARCHAR(15)"

    @staticmethod
    @handle_options
    def binary(size):
        if size:
            return f"BINARY({size})"

        return "BINARY"

    @staticmethod
    @handle_options
    def varbinary(size):
        if size:
            return f"VARBINARY({size})"

        return "VARBINARY(15)"

    @staticmethod
    @handle_options
    def tinyblob():
        return "TINYBLOB"

    @staticmethod
    @handle_options
    def tinytext():
        return "TINYTEXT"

    @staticmethod
    @handle_options
    def blob(length):
        if length:
            return f"BLOB({length})"

        return "BLOB"

    @staticmethod
    @handle_options
    def text(length):
        if length:
            return f"TEXT({length})"

        return "TEXT"

    @staticmethod
    @handle_options
    def mediumblob():
        return "MEDIUMBLOB"

    @staticmethod
    @handle_options
    def mediumtext():
        return "MEDIUMTEXT"

    @staticmethod
    @handle_options
    def longblob():
        return "LONGBLOB"

    @staticmethod
    @handle_options
    def longtext():
        return "LONGTEXT"

    @staticmethod
    @handle_options
    def enum(*args):
        arg_list = ', '.join(f"'{arg}'" for arg in args)
        return f"ENUM({arg_list})"

    @staticmethod
    @handle_options
    def set(*args):
        arg_list = ', '.join(f"'{arg}'" for arg in args)
        return f"SET({arg_list})"

    # Table functions

    @staticmethod
    def primary_key(*args):
        return f"PRIMARY KEY ({', '.join(args)})"

    @staticmethod
    def unique(*args, constraint_name=None):
        if constraint_name is None:
            constraint_name = '_'.join(args)

        return f"CONSTRAINT {constraint_name} UNIQUE ({', '.join(args)})"

    @staticmethod
    def foreign_key(constraint_name, table, local_keys, foreign_keys):
        return f"CONSTRAINT {constraint_name} FOREIGN KEY ({', '.join(local_keys)}) REFERENCES {table}({', '.join(foreign_keys)})"
