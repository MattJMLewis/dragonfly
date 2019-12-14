from dragonfly import models


class Article(models.Model):

    title = models.VarCharField(length=50, unique=True)
    text = models.TextField()
