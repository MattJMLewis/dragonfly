from dragonfly.db import models


class User(models.Model):
    username = models.VarCharField(null=False)
    email = models.VarCharField(length=50)
    password = models.VarCharField(length=128)
    salt = models.VarCharField(length=32)
    session_id = models.VarCharField(length=64, null=True)