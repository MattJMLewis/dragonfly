import json

from dragonfly.db.database import DB
from dragonfly.db.models.fields import PrimaryKey
from dragonfly.request import request
from dragonfly.response import Response


class Model(object):
    """A way to easily interact with rows in a table."""

    def __init__(self, data=None):
        """
        By providing data to the constructor the class is converted from an object that represents the Model's table to
        a row in the Model's table.

        :param data: The data to initialise the class with if it represents a row in the database.
        """

        # By default it is not a row
        self.is_row = False

        # Retrieve the types that were defined in the user defined model and set the primary key for the table
        self.types = {}
        self.primary_key = []
        self.composite = False

        for (key, value) in self.__class__.__dict__.items():
            if not key.startswith("__") and not key == 'Meta':

                if not callable(value):
                    self.types[key] = value

                    if value.default_parameters['primary_key']:
                        self.primary_key.append(key)

        self.meta = {}

        try:
            for (key, value) in self.__class__.__dict__['Meta'].__dict__.items():
                if not key.startswith("__"):
                    self.meta[key] = value

                    if isinstance(value, PrimaryKey):
                        self.primary_key = list(value.args)
        except KeyError:
            pass

        if len(self.primary_key) > 1:
            self.composite = True

        # Generate the table name if it has not been defined
        if 'table_name' not in self.meta.keys():
            self.meta['table_name'] = self.__class__.__name__.lower() + 's'

        # Shortcut
        self.types_keys = self.types.keys()

        # Only used if class is a row
        self.database_values = {}
        self.new_values = {}

        # Default DB attributes to None
        for key in self.types_keys:
            setattr(self, key, None)

        # Shortcut to interact with DB
        self.db = DB().table(self.meta['table_name'])

        # Set the class attributes to the given data (if present), converting the class to a row
        if data is not None:
            self.is_row = True
            self.data_to_attributes(data)

    def __str__(self):
        if self.is_row:
            string = f"{self.__class__.__name__}\n"
            for key in self.types_keys:
                string += f"{key}: {self.__dict__[key]}\n"

            return string

        else:
            return f"{self.__class__.__name__} instance. No data is bound"

    def create(self, create_dict):
        self.db.insert(create_dict)

        if not self.composite:
            create_dict[self.primary_key[0]] = self.db.last_insert_id

        return self.data_to_model([create_dict])[0]

    def first(self):
        """Get the first row in the table."""
        return self.data_to_model([self.db.first()])[0]

    def get(self):
        """Get all rows in the table that correspond to the other specified selectors."""
        return self.data_to_model(self.db.get())

    def all(self):
        """Get all rows in the database."""
        return self.data_to_model(self.db.get())

    def find(self, primary_key):
        """
        Find a row by passing in the value of the desired row's primary key.

        Note that if you would like to find a model with more than one key pass through a dictionary containing the
        column and value.

        :example:
            ``Article().find({'id': 1, 'author': 1})``
        """
        if isinstance(primary_key, dict):
            self.db.multiple_where(primary_key)
        else:
            self.db.where(self.primary_key[0], '=', primary_key)

        return self.first()

    def select(self, *args):
        """Same as the `DB` class `select` method."""
        self.db.select(*args)

    def where(self, column, comparator, value):
        """Same as the :class:`DB <dragonfly.db.database.DB>` class :meth:`where <dragonfly.db.database.DB.where>` method."""

        self.db.where(column, comparator, value)

    def paginate(self, size, to_json=False):
        """
        Paginates the data in the table by the given size.

        Note that if ``to_json`` is ``True`` a response will be returned containing the appropriate JSON, otherwise a list
        of rows that correspond to the page requested will be returned (the page number is known from the request
        object).

        :param size: The number of rows on each page
        :type size: int

        :param to_json: If the function should return a JSON response, default is False
        :type to_json: bool

        """
        if not bool(request.get_data()):
            page_number = 1
        else:
            page_number = request.get_data()['page'][0]

        result = self.data_to_model(self.db.chunk(int(page_number), size))

        if to_json:
            json_rep = json.dumps([row.get_attributes() for row in result])
            return Response(content=json_rep, content_type='application/json')

        return result

    def update(self, update_dict):

        if not all(item in self.types_keys for item in update_dict.keys()):
            raise Exception("Mismatch between model defined columns and given columns")

        for key in update_dict.keys():
            self.__dict__[key] = update_dict[key]

        self.save()

        return self

    def save(self):
        """
        Permeate the changes to the model attributes, to the database.
        """
        # Iterate over each new attribute (check if changed) and validate using Field class. Then save to DB
        self.new_values = {}

        for key in self.types_keys:
            self.new_values[key] = self.__dict__[key]

        self.db.multiple_where(self.database_values).update(self.new_values)

    def delete(self):
        self.db.multiple_where(self.database_values).delete()

    def data_to_model(self, data):
        """Starts the process of converting data from the database to model instances.

        :param data: The data to convert
        :return:
        """

        if self.is_row:
            raise Exception("A data bound class cannot be rebound to more data")

        # Create new class instances passing in the given data
        collection = [self.__class__(row) for row in data]

        return collection

    def data_to_attributes(self, data):
        """Converts the given data to class attributes in the class instance.

        The given data (from the database) is first converted to its equivalent python type and then assigned to the
        class dictionary as well as a ``database_values`` dictionary that is used to retrieve the correct row from the
        database when updating the model.

        :param data: The data to assign to the model instance
        :return:
        """

        if not self.is_row:
            raise Exception("A non data bound class cannot be bound to data without being converted")

        # Ensure that the retrieved data and the defined model match
        if not data.keys() == self.types_keys:
            raise Exception("Mismatch between model defined columns and database columns")

        for key, value in self.types.items():
            # In the future the to_python_type() method on each field class can be uses to convert to the correct type
            # when the given DB package (e.g mysqldb) does not do it by default
            value = data[key]

            # Assign the given data values to a class attribute (using __dict__)
            self.__dict__[key] = value

            # Store a back up of the data values so the row can be found when updating the model
            self.database_values[key] = value

    def get_attributes(self):
        attributes = {}
        for key in self.types_keys:
            attributes[key] = self.__dict__[key]

        return attributes
