from dragonfly.db import models


class Session(models.Model):
    session_id = models.VarCharField(length=64)
    name = models.VarCharField(length=50)
    value = models.VarCharField(length=50)