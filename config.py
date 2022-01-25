import json
from os import environ as env


app_secret = env.get("APP_KEY")
id = 915274079274164234
secret = env.get("SECRET")
token = env.get("TOKEN")
host = env.get("HOST")
invite = "https://discord.com/api/oauth2/authorize?client_id=915274079274164234&permissions=545394785527&scope=bot"
supp = "https://discord.gg/UhThVBWWqA"
support = 900078273021751296
postgres_database_url = env.get("psql")


from tortoise.backends.base.config_generator import expand_db_url


tortoise = {
  "connections": {
    "default": expand_db_url(postgres_database_url),
  },
  "apps": {
    "default": {
      "models": [
        "db"
      ]
    }
  }
}

del expand_db_url

tortoise["connections"]["default"]["credentials"]["ssl"] = "disable"


async def c_onnect():
  from tortoise import Tortoise
  await Tortoise.init(config = tortoise)
  await Tortoise.generate_schemas(safe=True)
  from db import Kaeya
  d=await Kaeya.all()
  a={}
  for i in d:
    val = i.value
    if i.key=="tops": val=json.loads(val)
    try: val=int(val)
    except: val=val
    a[i.key]=val
  globals().update(a)

def connect():
  import asyncio
  asyncio.get_event_loop() \
  .run_until_complete(c_onnect())

async def update(k,v):
  from db import Kaeya
  mod = Kaeya.get_or_none(key=k)
  if k=="tops" and isinstance(v,dict): v=json.dumps(v)
  try:
    if not await mod: return False
    await mod.update(value=str(v))
  except: return False

  try: v=int(v)
  except: v=v

  if k=="tops": v=json.loads(v)

  try: globals()[k]=v
  except: return False
  return True
