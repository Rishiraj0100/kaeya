from tortoise import fields, models


class Kaeya(models.Model):
  class meta:
    table = "bot_kaeya"

  key   = fields.TextField()
  value = fields.TextField()
