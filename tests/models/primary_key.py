from dragonfly import models


class PrimaryKey(models.Model):

    string = models.CharField(primary_key=True)
    another_string = models.CharField()

    class Meta:
        id = False
        timestamps = False
        primary_key = models.PrimaryKey('another_string')
