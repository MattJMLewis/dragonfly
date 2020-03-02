import datetime
import json

from dragonfly.db.database import DB
from dragonfly.db.models.fields import PrimaryKey, IntField, TimestampField
from dragonfly.request import request
from dragonfly.response import Response


def default(o):
    """
    Function from StackOverflow - https://stackoverflow.com/questions/12122007/python-json-encoder-to-support-datetime
    """
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


class Model(object):
    """A way to easily interact with rows in a table."""

    def __init__(self, data=None):
        """
        By providing data to the constructor the class is converted from an object that represents the Model's table to
        a row in the Model's table.

        :param data: The data to initialise the class with if it represents a row in the database.
        """

        # If this value is true then any data returned from the database will not have all the model fields. As such a
        # model instance cannot be created from that data. This field is thus needed to determine when this has happened
        # and to return a dictionary of data instead of attempting (and failing) to instantiate a model for it.
        self.__has_select = False

        # By default it is not a row
        self.__is_row = False

        # Retrieve the types that were defined in the user defined model and set the primary key for the table
        self.fields = {}
        self.primary_key = []
        self.__composite = False

        self._relationships = {}

        for (key, value) in self.__class__.__dict__.items():

            # Make sure not an inbuilt method or in the 'Meta' subclass
            if not key.startswith("__") and not key == 'Meta':

                # Make sure not a function
                if not callable(value):
                    # Must be a field type so add to types dictionary
                    self.fields[key] = value

                    # If the field has the 'primary_key' attribute set to true then add to list of primary keys
                    if value.default_parameters['primary_key']:
                        self.primary_key.append(key)

        # Retrieve all data from the 'Meta' subclass (if present)
        self.meta = {}

        try:
            for (key, value) in self.__class__.__dict__['Meta'].__dict__.items():
                if not key.startswith("__"):
                    self.meta[key] = value

                    # Retrieve any defined primary keys in 'Meta' subclass. Note that this will override any field defined primary keys
                    if isinstance(value, PrimaryKey):
                        self.primary_key = list(value.fields)
        except KeyError:
            pass

        try:
            # If the 'id' bool is defined and set to 'True' in 'Meta' class add id field
            if self.meta['id'] is True:
                self.fields['id'] = IntField(unsigned=True, auto_increment=True, primary_key=True)
                self.primary_key.append('id')
        except KeyError:
            # If 'id' bool is not present in 'Meta' class add id field (assuming id field is wanted by default)
            self.fields['id'] = IntField(unsigned=True, auto_increment=True, primary_key=True)
            self.primary_key.append('id')

        # The same as a above but for 'created_at' and 'updated_at' timestamps
        try:
            if self.meta['timestamps'] is True:
                self.fields['created_at'] = TimestampField(default='CURRENT_TIMESTAMP', null=False)
                self.fields['updated_at'] = TimestampField(default='NOW()', on="UPDATE NOW()", null=False)
        except KeyError:
            self.fields['created_at'] = TimestampField(default='CURRENT_TIMESTAMP', null=False)
            self.fields['updated_at'] = TimestampField(default='NOW()', on="UPDATE NOW()", null=False)

        if len(self.primary_key) > 1:
            self.__composite = True

        # Generate the table name if it has not been defined
        if 'table_name' not in self.meta.keys():
            # TODO split at capital and add underscore
            self.meta['table_name'] = self.__class__.__name__.lower() + 's'

        self.meta['primary_key'] = self.primary_key

        # Shortcut
        self.__fields_keys = self.fields.keys()

        # Only used if class is a row
        self._database_values = {}
        self.__new_values = {}

        # Default DB attributes to None
        for key in self.__fields_keys:
            setattr(self, key, None)

        # Shortcut to interact with DB
        self.__db = DB().table(self.meta['table_name'])

        # Set the class attributes to the given data (if present), converting the class to a row
        if data is not None:
            self.__is_row = True
            self.__data_to_attributes(data)

    def __str__(self):
        if self.__is_row:
            string = f"{self.__class__.__name__}\n"
            for key in self.__fields_keys:
                string += f"{key}: {self.__dict__[key]} \n"

            return string

        else:
            return f"{self.__class__.__name__} instance. No data is bound"

    def __bool__(self):
        """
        Returns 'True' if the class is a row and 'False' if not.

        :return: If the Model is a row
        """
        if self.__is_row:
            return True

        return False

    def create(self, create_dict):
        """
        Creates a new row in the table and returns a model representation of this row.

        :param create_dict: The values to create the new row with
        :type create_dict: dict

        :return: A list of object models
        :rtype: list
        """

        self.__db.insert(create_dict)

        # Composite keys have not been implemented
        if not self.__composite:
            # Get id of new row to update timestamp data.
            create_dict[self.primary_key[0]] = self.__db.last_insert_id

        # It is not possible to be certain that a timestamp generated in Python will be the same as the one generated in
        # the table. Thus the timestamp fields are retrieved from the table and a new model class instantiated with them
        # along with the given 'create_dict' data.
        try:
            if self.meta['timestamps'] is True:
                timestamp_values = self.__db.custom_sql(
                    f"SELECT created_at, updated_at FROM {self.meta['table_name']} WHERE {self.primary_key[0]} = {self.__db.last_insert_id}")[
                    0]
                create_dict['created_at'] = timestamp_values['created_at']
                create_dict['updated_at'] = timestamp_values['updated_at']
        except KeyError:
            timestamp_values = self.__db.custom_sql(
                f"SELECT created_at, updated_at FROM {self.meta['table_name']} WHERE {self.primary_key[0]} = {self.__db.last_insert_id}")[
                0]
            create_dict['created_at'] = timestamp_values['created_at']
            create_dict['updated_at'] = timestamp_values['updated_at']

        return self.__data_to_model([create_dict])[0]

    def first(self):
        """
        Get the first row in the table.

        :return: An object model
        :rtype: :class:`Model <dragonfly.db.models.model.Model>`
        """
        return self.__data_to_model([self.__db.first()])[0]

    def get(self):
        """
        Get all rows in the table.

        :return: An object model
        :rtype: list
        """
        return self.__data_to_model(self.__db.get())

    def all(self):
        """
        Get all rows in the table .

        :return: A list object models
        :rtype: list
        """
        return self.__data_to_model(self.__db.get())

    def find(self, primary_key):
        """
        Find a row by passing in the value of the row's primary key.

        Note that if you would like to find a model with more than one key pass through a dictionary containing the
        column and value.

        :example:
            ``Article().find({'id': 1, 'author': 1})``

        :param primary_key: The value of the primary key to find.
        :type primary_key: int

        :return: An object model that has the given value as its primary key
        :rtype: :class:`Model <dragonfly.db.models.model.Model>`
        """
        if isinstance(primary_key, dict):
            self.__db.multiple_where(primary_key)
        else:
            self.__db.where(self.primary_key[0], '=', primary_key)

        return self.first()

    def select(self, *args):
        """
        Same as the  :class:`DB <dragonfly.db.database.DB>` class :meth:`select<dragonfly.db.database.DB.select>` method. Note that a dictionary will be returned as a model cannot be represented with incomplete data.

        :param args: A list of columns to select

        :return: This model object
        :rtype: :class:`Model <dragonfly.db.models.model.Model>`
        """
        self.__db.select(*args)
        self.__has_select = True

        return self

    def where(self, column, comparator, value):
        """
        Same as the :class:`DB <dragonfly.db.database.DB>` class :meth:`where <dragonfly.db.database.DB.where>` method.

        :param column: The column in the database to check the value for
        :type column: str

        :param comparator: The comparison operator e.g. =
        :type comparator: str

        :param value: The value to test for

        :return: This model object
        :rtype: :class:`Model <dragonfly.db.models.model.Model>`
        """

        self.__db.where(column, comparator, value)

        return self

    def multiple_where(self, where_dict):
        """
        Select a row from the table using multiple values/columns

        :param where_dict: A dictionary where the key is the column in the table and the value is the value in the table.
        :type where_dict: dict


        :return This model object
        :rtype: :class:`Model <dragonfly.db.models.model.Model>`
        """
        self.__db.multiple_where(where_dict)

        return self

    def paginate(self, size, to_json=False):
        """
        Paginates the data in the table by the given size.

        Note that if ``to_json`` is ``True`` a :class:`Response <dragonfly.response.Response>` will be returned containing the appropriate JSON. Otherwise a list
        of rows that correspond to the page requested will be returned (the page number is known from the request
        object).

        :param size: The number of rows on each page
        :type size: int

        :param to_json: If the function should return a JSON response, default is False
        :type to_json: bool

        :return: A tuple containing a dictionary if results and a dictionary contaning meta information
        :rtype: tuple

        """
        if not bool(request.get_data()):
            page_number = 1
        else:
            page_number = request.get_data()['page'][0]

        result, meta = self.__db.chunk(int(page_number), size)

        if result is None:
            return None, None

        result = self.__data_to_model(result)

        if to_json:
            meta['data'] = [row.__get_field_values() for row in result]

            return Response(content=json.dumps(meta, default=default), content_type='application/json')

        return result, meta

    def update(self, update_dict):
        """
        Update this model with the given values.

        :param update_dict: Update the given columns (key) with the given values
        :type update_dict: dict

        :return: This model object
        :rtype: :class:`Model <dragonfly.db.models.model.Model>`
        """

        # Check to see if any given keys in the dictionary do not match the model fields/columns
        if not all(item in self.__fields_keys for item in update_dict.keys()):
            raise Exception("Mismatch between model defined columns and given columns")

        for key in update_dict.keys():
            self.__dict__[key] = update_dict[key]

        self.save()

        return self

    def save(self):
        """
        Permeate the changes made to the Python model to the database.
        """

        # Iterate over each new attribute (check if changed) and validate using Field class. Then save to DB
        self.__new_values = {}

        for key in self.__fields_keys:
            if self.__dict__[key] is not None:
                self.__new_values[key] = self.__dict__[key]

        self._database_values = {k: v for k, v in self._database_values.items() if v is not None}

        self.__db.multiple_where(self._database_values).update(self.__new_values)

    def delete(self):
        """Delete this row from the database ."""
        self.__db.multiple_where(self._database_values).delete()

    def to_dict(self):
        """
        Return a dictionary equivalent of this row.

        :return: A dictionary equivalent of this row
        :rtype: dict
        """
        if not self.__is_row:
            raise Exception("A non data bound class cannot be converted to a dictionary")

        return self._database_values

    def __data_to_model(self, data):
        """Starts the process of converting data from the database to model instances.

        :param data: The data to convert
        :type: list

        :return: A list of instantiated model objects
        :rtype: list
        """

        # Return a dict if true and thus not all fields present.
        if self.__has_select:
            self.__has_select = False
            return data

        if self.__is_row:
            raise Exception("A data bound class cannot be rebound to more data")

        # Create new class instances passing in the given data
        collection = [self.__class__(row) for row in data]

        return collection

    def __data_to_attributes(self, data):
        """Converts the given data to class attributes in the class instance.

        The given data (from the database) is first converted to its equivalent python type and then assigned to the
        class dictionary as well as a ``database_values`` dictionary that is used to retrieve the correct row from the
        database when updating the model.

        :param data: The data to assign to the model instance
        """

        if not self.__is_row:
            raise Exception("A non data bound class cannot be bound to data without being converted")

        for k, v in self.fields.items():
            if v.default_parameters['null']:
                if k not in data:
                    data[k] = None

        # Ensure that the retrieved data and the defined model match
        if not data.keys() == self.__fields_keys:
            raise Exception("Mismatch between model defined columns and database columns")

        for key, value in self.fields.items():
            # In the future the to_python_type() method on each field class can be uses to convert to the correct type
            # when the given DB package (e.g mysqldb) does not do it by default
            value = data[key]

            # Assign the given data values to a class attribute (using __dict__)
            self.__dict__[key] = value

            # Store a back up of the data values so the row can be found when updating the model
            self._database_values[key] = value

    def __get_field_values(self):
        """
        Returns the values of the model fields.

        :return: Dictionary containing the fields of the model and the values.
        :rtype: dict
        """
        attributes = {}
        for key in self.__fields_keys:
            attributes[key] = self.__dict__[key]

        return attributes

    def add_relationship(self, relationship_class, update=False):
        """
        Adds a relationship to another model to this model instance using the relationship classes. Note that the method
        will cache the values of a relationship unless update is set to true.

        :param relationship_class: An instantiated relationship class.
        :type relationship_class: :class:`Relationship <dragonfly.db.models.relationships.Relationship>`

        :param update: If the method should retrieve fresh data from the database.
        :type update: bool

        :return: The retrieved, related, model(s).
        :rtype: :class:`Relationship <dragonfly.db.models.relationships.Relationship>`
        """
        target_name = relationship_class.target_name

        if update:
            self._relationships[target_name] = relationship_class.delayed_init(self._database_values,
                                                                               self.meta)
            return self._relationships[target_name]

        try:
            return self._relationships[target_name]
        except KeyError:
            self._relationships[target_name] = relationship_class.delayed_init(self._database_values,
                                                                               self.meta)
            return self._relationships[target_name]
