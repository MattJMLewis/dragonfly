from dragonfly import models


class Timestamp(models.Model):

    class Meta:
        id = False
        timestamps = False

