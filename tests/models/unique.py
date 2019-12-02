from dragonfly import models


class Unique(models.Model):

    string = models.CharField(unique=True)

    class Meta:
        id = False
        timestamps = False
