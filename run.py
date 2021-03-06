import config, os

from quart_discord import DiscordOAuth2Session, requires_authorization as auth, Unauthorized
from quart import Quart, redirect, url_for, render_template as render, request, jsonify, abort


app = Quart(__name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

app.config["SECRET_KEY"] = config.app_secret
app.config["DISCORD_CLIENT_ID"] = config.id
app.config["DISCORD_CLIENT_SECRET"] = config.secret
app.config["DISCORD_BOT_TOKEN"] = config.token
app.config["DISCORD_REDIRECT_URI"] = config.host + "callback"

discord = DiscordOAuth2Session(app)

@app.route("/")
async def index():
  return await render("index.html",logged=await discord.authorized,top_servers=config.tops)

@app.route("/invite/")
async def invite():
  return redirect("https://discord.com/api/oauth2/authorize?client_id=915274079274164234&permissions=545394785527&scope=bot")

@app.route("/login")
async def login():
  red = request.args.get("redirect","/me")
  return await discord.create_session(scope=["identify","guilds","guilds.join","connections","guilds.members.read"],data={"redirect": red})

@app.route("/callback/")
async def callback():
  if not requests.args.get("code"): return redirect("/")

  return redirect((await discord.callback()).get("redirect","/"))

@app.route("/me/")
@auth
async def me():
  user = await discord.fetch_user()
  return f"""
<html>
<head>
<title>{user.name}</title>
</head>
<body><img src='{user.avatar_url or user.default_avatar_url}' />
<p>Is avatar animated: {str(user.is_avatar_animated)}</p>
<a href={url_for("connections")}>Connections</a>
<br />
</body>
</html>
"""

@app.route("/me/connections/")
@auth
async def connections():
  user = await discord.fetch_user()
  connections = await discord.fetch_connections()
  return f"""
<html>
<head>
<title>{user.name}</title>
</head>
<body>
{str([f"{connection.name} - {connection.type}" for connection in connections])}
</body>
</html>
"""

@app.route("/me/servers/")
@auth
async def user_guilds():
  guilds = await discord.fetch_guilds()
  def _(g):
    r=(f'<img src="{g.icon_url}">' if g.icon_url else "")+"<br />"
    if g.permissions.administrator: r+="[ADMIN] "
    r += g.name
    return r

  return "<br />".join([_(g) for g in guilds])

@app.route("/logout/")
async def logout():
  if await discord.authorized: discord.revoke()
  return redirect(url_for(".index"))

@app.route("/join/")
async def join():
  if await discord.authorized:
    await (await discord.fetch_user()).add_to_guild(config.support)
    return redirect(request.args.get("redirect","/"))

  return redirect("/discord")

@app.route("/discord/")
async def supp(): return redirect(config.supp)

@app.errorhandler(Unauthorized)
async def unauth(err):
  return redirect("/login")

@app.route("/api/dev/update", methods=["GET","POST"])
async def api_dev_update():
  if request.headers.get("Authorization","&$")!=config.app_secret:
    return abort(403) # 403: forbidden

  if request.method.lower()=="get":
    from db import Kaeya

    ret = {"settings": {}}
    for i in await Kaeya.all(): ret["settings"][i.key]=i.value
  else:
    ret=[]
    for k,v in request.json.items(): ret.append(await config.update(k,v))
    ret = {"success": all(ret)}

  return jsonify(ret)


app.run("0.0.0.0",port=8080,debug=True)
