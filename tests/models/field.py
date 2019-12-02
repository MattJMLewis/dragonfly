from dragonfly import models


class Field(models.Model):

    # Numeric types

    empty_bit = models.BitField()
    bit = models.BitField(length=10)

    empty_tiny_int = models.TinyIntField()
    tiny_int = models.TinyIntField(length=10)

    bool = models.BoolField()

    empty_small_int = models.SmallIntField()
    small_int = models.SmallIntField(length=10)

    empty_medium_int = models.MediumIntField()
    medium_int = models.MediumIntField(length=10)

    empty_int = models.IntField()
    int = models.IntField(length=10)

    empty_big_int = models.BigIntField()
    big_int = models.BigIntField(length=10)

    empty_decimal = models.DecimalField()
    decimal = models.DecimalField(5, 2)

    empty_float = models.FloatField()
    float = models.FloatField(10)

    empty_double = models.DoubleField()
    double = models.DoubleField(5, 2)

    # Date and time types

    date = models.DateField()

    empty_datetime = models.DateTimeField()
    datetime = models.DateTimeField(6)

    empty_timestamp = models.TimestampField()
    timestamp = models.TimestampField(fsp=6, on="UPDATE CURRENT_TIMESTAMP")

    empty_time = models.TimeField()
    time = models.TimeField(6)

    year = models.YearField()





    class Meta:
        id = False
        timestamps = False
