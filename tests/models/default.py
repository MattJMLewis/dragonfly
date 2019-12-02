from dragonfly import models


class Default(models.Model):

    string = models.CharField(default="'testing'")
    second_string = models.CharField(default=1)

    class Meta:
        id = False
        timestamps = False
