import discord
from discord.ext import commands
import asyncio
import time
import random
import requests
import feedparser
import os

COMMAND_PREFIX = "."
Client = discord.Client()
client = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    description="Hello! I'm python test bot by risualiser#1706"
)

@client.event
async def on_ready():
    print("Logged in as {0}#{1}".format(client.user.name, client.user.discriminator))
    global READY_TIME
    READY_TIME = time.time()
    await client.change_presence(game=discord.Game(name="{0}help".format(COMMAND_PREFIX)))

@client.command(pass_context=True)
async def invite(ctx):
    """Invite me to your server!"""
    invite_link = "https://discordapp.com/api/oauth2/authorize?client_id=" + client.user.id + "&scope=bot&permissions=0"
    await client.say("You can invite me on your server by this link:\n" + invite_link)

@client.command(pass_context=True, hidden=True)
async def ping(ctx):
    """Pong!"""
    p_msg = await client.say("Pong!")
    diff = p_msg.timestamp - ctx.message.timestamp
    await client.edit_message(p_msg, "Pong! {0} sec".format(diff))
	

@client.command(pass_context=True, hidden=True)
async def uptime(ctx):
    """How long have I been working."""
    now = time.time()
    diff = int(now - READY_TIME)

    t_max = [60, 60, 24]

    for i in range(0, len(t_max)):
        m = t_max[i]
        t_max[i] = diff % m
        diff = (diff - t_max[i]) // m
    t_max.append(diff)

    time_words = [
        ["second", "seconds"],
        ["minute", "minutes"],
        ["hour", "hours"],
        ["day", "days"]
    ]

    t_parts = []
    for i in range(0, len(t_max)):
        n = t_max[i]
        if n:
            t_word = time_words[i][0] if n == 1 else time_words[i][1]
            t_parts.append("{0} {1}".format(n, t_word))
    t_parts.reverse()

    await client.say("I've been working for {0}.".format(", ".join(t_parts)))

@client.command(pass_context=True, hidden=True)
async def avatar(ctx):
    """Show your avatar."""
    user = ctx.message.author  # change this later to any other user
    if user.avatar_url:
        if user.avatar_url.find(".gif") == -1:
            avatar_template = "https://cdn.discordapp.com/avatars/{0}/{1}.png?size=2048"
        else:
            avatar_template = "https://cdn.discordapp.com/avatars/{0}/{1}.gif?size=2048"
        embed = discord.Embed(
            title=user.display_name
        )
        embed.set_image(url=avatar_template.format(user.id, user.avatar))
        await client.say(embed=embed)

@client.command(pass_context=True)
async def coin(ctx):
    """Flip the coin."""
    c = random.randint(0, 1)
    if c:
        await client.say("Heads!")
    else:
        await client.say("Tails!")

@client.command(pass_context=True)
async def whensu(ctx):
    """When new series, CN?"""
    r = requests.get("https://www.episodate.com/api/show-details?q=steven-universe")
    if 200 <= r.status_code < 300:
        api_data = r.json()
        countdown = api_data["tvShow"]["countdown"]
        if countdown:
            await client.say(api_data["tvShow"]["countdown"])
        else:
            await client.say("Who knows?")

@client.command(pass_context=True)
async def xkcd(ctx, num=""):
    """Random xkcd comic."""
    r = requests.get("https://xkcd.com/info.0.json")
    if 200 <= r.status_code < 300:
        api_data = r.json()
        random_num = random.randint(1, api_data["num"])
        if num:
            if num == "last":
                c = "https://xkcd.com/info.0.json"
            else:
                try:
                    n = int(num)
                    c = "https://xkcd.com/{0}/info.0.json".format(n)
                except:
                    c = "https://xkcd.com/{0}/info.0.json".format(random_num)
        else:
            c = "https://xkcd.com/{0}/info.0.json".format(random_num)

    if c:
        r = requests.get(c)
        if 200 <= r.status_code < 300:
            comic_data = r.json()
            embed = discord.Embed(
                title="{0} (#{1})".format(comic_data["title"], comic_data["num"]),
                url="https://xkcd.com/{0}/".format(comic_data["num"])
            )
            embed.set_image(url=comic_data["img"])
            embed.set_footer(text=comic_data["alt"])
            await client.say(embed=embed)


@client.command(pass_context=True)
async def tho(ctx):
    """Random thought from r/Showerthoughts/."""
    f = feedparser.parse("https://www.reddit.com/r/Showerthoughts/.rss")
    # add request checking
    t_num = random.randint(1, len(f.entries) - 1)

    embed = discord.Embed(
        description=f.entries[t_num].title
    )
    embed.set_author(
        name=f.entries[t_num].author,
        url=f.entries[t_num].link,
        icon_url=f.feed.logo
    )

    await client.say(embed=embed)

@client.command(pass_context=True)
async def da(ctx, source="marreeps", n=1, *tags):
    """Pics from DeviantArt. Syntax: author amount tags."""
    source_link = "https://backend.deviantart.com/rss.xml?type=deviation&q=by%3A" + source + "+sort%3Atime+meta%3Aall"

    link_parts = [source_link]
    for t in tags:
        link_parts.append(t)
    source_link = "+".join(link_parts)

    f = feedparser.parse(source_link)
    # add request checking

    n = int(n)
    f_max = 10 if len(f.entries) >= 10 else len(f.entries)
    if n > f_max:
        n = f_max

    for i in range(0, n):
        num = n - 1 - i
        embed = discord.Embed(
            title=f.entries[num].title,
            url=f.entries[num].link
        )
        embed.set_image(url=f.entries[num].media_content[0]["url"])
        embed.set_footer(text=f.entries[num].published)
        await client.say(embed=embed)

		
client.run(os.environ.get("TOKEN", None))
