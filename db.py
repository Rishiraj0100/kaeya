from tortoise import fields, models


class Kaeya(models.Model):
  key   = fields.TextField()
  value = fields.TextField()
