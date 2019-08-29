from string import Template

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
            if key not in sql_to_var.keys():
                raise Exception("Invalid argument")

            key_tuple = sql_to_var[key]

            if key_tuple[1]:
                append += ' ' + key_tuple[0].substitute(parameter=kwargs[key])
            else:
                if kwargs[key]:
                    append += ' ' + key_tuple[0]

            del kwargs[key]

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
        return f"SMALLINT({length})"

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
        return f"DECIMAL({digits}, {decimal_places})"

    @staticmethod
    @handle_options
    def float(length):
        return f"FLOAT({length})"

    @staticmethod
    @handle_options
    def double(digits, decimal_places):
        return f"DOUBLE({digits}, {decimal_places})"

    # Date and time types

    @staticmethod
    @handle_options
    def date():
        return f"DATE"

    @staticmethod
    @handle_options
    def datetime(fsp=0):
        return f"DATETIME({fsp})"

    @staticmethod
    @handle_options
    def timestamp(fsp=0):
        return f"TIMESTAMP({fsp})"

    @staticmethod
    @handle_options
    def time(fsp=0):
        return f"TIME({fsp})"

    @staticmethod
    @handle_options
    def year():
        return f"YEAR"

    # String types

    @staticmethod
    @handle_options
    def char(size):
        return f"CHAR({size})"

    @staticmethod
    @handle_options
    def varchar(size):
        return f"VARCHAR({size})"

    @staticmethod
    @handle_options
    def binary(size):
        return f"BINARY({size})"

    @staticmethod
    @handle_options
    def varbinary(size):
        return f"VARBINARY({size})"

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
        return f"BLOB({length})"

    @staticmethod
    @handle_options
    def text(length):
        if length:
            return f"TEXT({length})"
        else:
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
        return f"ENUM({', '.join(args)})"

    @staticmethod
    @handle_options
    def set(*args):
        return f"SET({', '.join(args)})"

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
        return f"CONSTRAINT {constraint_name} FOREIGN KEY ({', '.join(local_keys)}) REFERENCES {table} ({', '.join(foreign_keys)})"
