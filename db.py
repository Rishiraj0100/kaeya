from tortoise import fields, models


class Kaeya(models.Model):
  class Meta:
    table = "bot_kaeya"

  key   = fields.TextField()
  value = fields.TextField()
