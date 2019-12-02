from dragonfly import models


class TableName(models.Model):

    class Meta:
        id = False
        timestamps = False
        table_name = 'different_name'
