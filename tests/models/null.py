from dragonfly import models
from dragonfly.db import models

class Null(models.Model):

    string = models.CharField(null=True)

    class Meta:
        id = False
        timestamps = False
