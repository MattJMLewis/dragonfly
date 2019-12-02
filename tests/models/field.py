from dragonfly import models


class Field(models.Model):

    # Numeric types

    empty_bit = models.BitField()
    nbit = models.BitField(length=10)

    empty_tiny_int = models.TinyIntField()
    ntiny_int = models.TinyIntField(length=10)

    nbool = models.BoolField()

    empty_small_int = models.SmallIntField()
    nsmall_int = models.SmallIntField(length=10)

    empty_medium_int = models.MediumIntField()
    nmedium_int = models.MediumIntField(length=10)

    empty_int = models.IntField()
    nint = models.IntField(length=10)

    empty_big_int = models.BigIntField()
    nbig_int = models.BigIntField(length=10)

    empty_decimal = models.DecimalField()
    ndecimal = models.DecimalField(5, 2)

    empty_float = models.FloatField()
    nfloat = models.FloatField(10)

    empty_double = models.DoubleField()
    ndouble = models.DoubleField(5, 2)

    # Date and time types

    ndate = models.DateField()

    empty_datetime = models.DateTimeField()
    ndatetime = models.DateTimeField(6)

    empty_timestamp = models.TimestampField()
    ntimestamp = models.TimestampField(on="UPDATE CURRENT_TIMESTAMP", default="CURRENT_TIMESTAMP")
    nn_timestamp = models.TimestampField(6, null=True)

    empty_time = models.TimeField()
    ntime = models.TimeField(6)

    nyear = models.YearField()

    # String types

    empty_varchar = models.VarCharField()
    nvarchar = models.VarCharField(length=10)

    empty_char = models.CharField()
    nchar = models.CharField(length=255)

    empty_binary = models.BinaryField()
    nbinary = models.BinaryField(length=10)

    ntiny_blob = models.TinyBlobField()

    ntiny_text_field = models.TinyTextField()

    empty_text = models.TextField()
    ntext = models.TextField(length=10)

    nmedium_blob = models.MediumBlob()

    nmedium_text = models.MediumText()

    nlong_blob = models.LongBlob()

    nenum = models.Enum("test", "test_one")

    nset = models.Set("test", "test_one")



    class Meta:
        id = False
        timestamps = False
