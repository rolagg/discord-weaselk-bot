import discord
from discord.ext import commands
import os
import asyncio
import time
import datetime
import random
import re
import requests
import feedparser
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
import urllib.request as urllib2
import io
import numpy as np
import colorsys


COMMAND_PREFIX = "."
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0"}

Client = discord.Client()
client = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    description="Hello! I'm python test bot by risualiser#1706"
)


def print_log(ctx):
    print("{0}#{1}: {2}".format(ctx.message.author.name, ctx.message.author.discriminator, ctx.message.content))

def req_soup(link):
    r = requests.get(link, headers=HEADERS)
    if 200 <= r.status_code < 300:
        return BeautifulSoup(r.text, "html.parser")
    else:
        return False

def shorten_desc(str, n=500):
    if n > 2047:
        n = 2047
    return (str[:n] + "…") if len(str) > n else str

def round2(value):
    return format(round(float(value), 2), '.2f')

rgb_to_hsv = np.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)

def shift_hue(arr, hout):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    h = hout
    r, g, b = hsv_to_rgb(h, s, v)
    arr = np.dstack((r, g, b, a))
    return arr


@client.event
async def on_ready():
    print("Logged in as {0}#{1}".format(client.user.name, client.user.discriminator))
    global READY_TIME
    READY_TIME = time.time()
    await client.change_presence(game=discord.Game(name="{0}help".format(COMMAND_PREFIX)))


@client.command(pass_context=True, hidden=True)
async def up(ctx):
    """How long have I been working."""
    print_log(ctx)

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
async def ping(ctx):
    """Pong!"""
    print_log(ctx)

    p_msg = await client.say("Pong!")
    diff = p_msg.timestamp - ctx.message.timestamp
    s = diff / datetime.timedelta(seconds=1)
    ms = diff / datetime.timedelta(milliseconds=1)
    d = s + (ms / 1000)
    await client.edit_message(p_msg, "Pong! {0} sec".format(d))


@client.command(pass_context=True, hidden=True)
async def test(ctx):
    """Test!"""
    print_log(ctx)

    await client.say("The test was completed successfully!")


@client.command(pass_context=True)
async def cl(ctx, count=1, mode="b", id=0, after=0):  # b - bot, a - admin (all), m - author (my)
    """Clear bot messages."""

    access_bot = False
    access_admin = False
    access_author = False
    text_rights_bot = False
    text_rights_user = False
    type = ctx.message.channel.type

    if count < 1:
        count = 1
    elif count > 100:
        count = 100

    target_m = ctx.message
    if id:
        try:
            target_m = await client.get_message(ctx.message.channel, id)
        except:
            target_m = ctx.message

    cl_before = target_m if not after else ctx.message
    cl_after = target_m if after else None

    if type == type.text:
        if ctx.message.author.server_permissions.manage_messages or ctx.message.author.server_permissions.administrator:
            text_rights_user = True
    if mode == "b":
        if type == type.private or type == type.group or (type == type.text and text_rights_user):
            access_bot = True
    if type == type.text and ctx.message.server.me.server_permissions.manage_messages:
        text_rights_bot = True
        if mode == "a" and text_rights_user:
            access_admin = True
        elif mode == "m":
            access_author = True

    if access_admin:
        async for msg in client.logs_from(ctx.message.channel, limit=count, before=cl_before, after=cl_after):
            await client.delete_message(msg)
    else:
        i = 0
        async for msg in client.logs_from(ctx.message.channel, limit=100, before=cl_before, after=cl_after):
            if i < count:
                if (access_author and msg.author == ctx.message.author) or (access_bot and msg.author == client.user):
                    await client.delete_message(msg)
                    i += 1
    if text_rights_bot:
        await client.delete_message(ctx.message)


@client.command(pass_context=True)
async def xk(ctx, num=""):
    """Random xkcd."""

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
                title="{0}".format(comic_data["safe_title"])
            )
            embed.set_author(
                name="#{0} ({1} {2})".format(
                    comic_data["num"],
                    datetime.date(1900, int(comic_data["month"]), 1).strftime("%b"),
                    comic_data["year"]
                ),
                url="https://xkcd.com/{0}/".format(comic_data["num"])
            )
            embed.set_image(url=comic_data["img"])
            embed.set_footer(text=comic_data["alt"])
            await client.say(embed=embed)


@client.command(pass_context=True)
async def hs(ctx, page=0, img_num=0):
    """Random Homestuck pic."""

    await client.send_typing(ctx.message.channel)
    if page:
        comic_num = page
    else:
        comic_num = random.randint(1, 8128)
    comic_link = "https://www.homestuck.com/story/{0}".format(comic_num)

    soup = req_soup(comic_link)
    if soup:
        content_container = soup.find("div", id="content_container")
        if content_container:
            imgs = soup.find("div", id="content_container").select("img.mar-x-auto.disp-bl")
        else:
            imgs = soup.select("img.mar-x-auto.disp-bl")

        desc = ""
        raw_desc_soup = soup.find("p", class_="type-rg")
        if raw_desc_soup:
            raw_desc = re.sub("<br[^<>]*>", "\n", str(raw_desc_soup))
            better_desc = BeautifulSoup(raw_desc, "html.parser").text
            desc = shorten_desc(better_desc, 500)

        try:
            embed = discord.Embed(
                title="{0} (#{1})".format(soup.find("h2", {"class": "type-hs-header"}).text, comic_num),
                url=comic_link,
                description=desc
            )
        except:
            embed = discord.Embed(
                title="#{0}".format(comic_num),
                url=comic_link
            )

        if imgs:
            if img_num:
                i_n = img_num
            else:
                i_n = random.randint(1, len(imgs))
            embed.set_image(
                url=imgs[i_n - 1]["src"]
            )
        else:
            embed.set_footer(
                text="It's probably flash."
            )

        try:
            await client.say(embed=embed)
        except:
            await client.say("<{0}>".format(comic_link))
            if imgs:
                await client.say(imgs[i_n]["src"])


@client.command(pass_context=True)
async def ud(ctx, *words):
    """Urban Dictionary."""

    if words:
        word = " ".join(words)
    else:
        word = "test"
    r = requests.get("https://api.urbandictionary.com/v0/define?term={0}".format(word))
    if 200 <= r.status_code < 300:
        api_data = r.json()
        num = 0
        found = False
        i = 0
        while num == 0 and not found:
            if api_data["list"][i]["word"].lower() == word.lower():
                found = True
                num = i
            if i == len(api_data["list"]) - 1:
                found = True
            i += 1

        w = api_data["list"][num]

        definition = shorten_desc(w["definition"], 1500)
        if w["example"]:
            example = shorten_desc(w["example"], 500)

        desc = "{0}\n\n*{1}*".format(definition, example) if w["example"] else definition
        embed = discord.Embed(
            title=w["word"],
            url=w["permalink"],
            description=re.sub("[[\]]", "**", desc)
        )
        embed.set_footer(
            text="👍 {0} 👎 {1}".format(w["thumbs_up"], w["thumbs_down"])
        )
        await client.say(embed=embed)


@client.command(pass_context=True)
async def su(ctx):
    """Date of new Steven Universe."""

    await client.send_typing(ctx.message.channel)
    soup = req_soup("https://old.reddit.com/r/stevenuniverse/")
    if soup:
        st = soup.find("a", {"href": "#y-sche"})
        if st:
            embed = discord.Embed(
                description=st.find_parent("h1").find_next_sibling("ul").li.contents[0]
            )
            embed.set_author(
                name=st.find_parent("h1").find_next_sibling("h3").contents[0]
            )
            await client.say(embed=embed)
        else:
            r = requests.get("https://www.episodate.com/api/show-details?q=steven-universe")
            if 200 <= r.status_code < 300:
                api_data = r.json()
                c = "Probably {0} UTC".format(api_data["tvShow"]["countdown"])
                if c:
                    await client.say(c)
                else:
                    await client.say("Who knows?")


@client.command(pass_context=True)
async def da(ctx, author="ikimaru-art", amount="1", *tags):
    """Pics from DeviantArt."""

    source_link = "https://backend.deviantart.com/rss.xml?type=deviation&q=by%3A{0}+sort%3Atime+meta%3Aall".format(author)
    link_parts = [source_link]
    need_orig = False
    need_fast = False

    n = amount
    try:
        n = int(n)
    except ValueError:
        link_parts.append(n)
        n = 1

    for i in range(0, len(tags)):
        t = tags[i]
        if t == "gif":
            need_orig = True
        link_parts.append(t)

    if len(link_parts) > 1:
        if link_parts[1] == "orig":
            need_orig = True
            link_parts.remove("orig")
        elif link_parts[1] == "fast":
            need_fast = True
            link_parts.remove("fast")

    source_link = "+".join(link_parts)

    f = feedparser.parse(source_link)

    f_max = 10 if len(f.entries) >= 10 else len(f.entries)
    if n > f_max:
        n = f_max
    elif n < 1:
        n = 1

    for num in range(n - 1, -1, -1):
        await client.send_typing(ctx.message.channel)

        entry = f.entries[num]

        try:
            if entry.media_thumbnail:
                m_thumb = entry.media_thumbnail[0]["url"]
        except:
            m_thumb = ""

        img_link = entry.media_content[0]["url"]
        if not need_fast and m_thumb:
            if need_orig or img_link.find("pre00.deviantart.net") != -1 or img_link == m_thumb:
                soup = req_soup(entry.link)
                if soup:
                    img_search = soup.find("div", {"data-gmiclass": "DeviationPageView"}).select("img.dev-content-full")
                    if img_search:
                        img_link = img_search[0]["src"]

            raw_desc = re.sub(r"<br.*?>", r"\n", entry.description, flags=re.DOTALL)
            raw_desc = re.sub(r"<img[^>]*title=\"(.*?)\".*?>", r"\1", raw_desc, flags=re.DOTALL)
            raw_desc = re.sub(r"<a[^>]*title=\"(.*?)\".*?</a>", r"\1", raw_desc, flags=re.DOTALL)
            b_desc = BeautifulSoup(raw_desc, "html.parser").text
            b_desc = re.sub(r"\n\s+\n", r"\n\n", b_desc)
            b_desc = re.sub(r"\n{3,}", r"\n", b_desc)
            desc = shorten_desc(b_desc, 500)

            embed = discord.Embed(
                url=img_link,
                description=desc,
                timestamp=datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
            )
            embed.set_author(
                name=entry.title,
                url=entry.link
            )
            embed.set_image(
                url=img_link
            )
            embed.set_footer(
                icon_url=entry.media_credit[1]["content"],
                text=entry.media_credit[0]["content"]
            )
            await client.say(embed=embed)
        else:
            await client.say(entry.link)


@client.command(pass_context=True)
async def tb(ctx, author="discount-supervillain", amount="1", *tags):
    """Posts from Tumblr."""

    tag_words = ""
    if tags:
        tag_words = "-".join(tags)
    n = amount
    try:
        n = int(n)
    except ValueError:
        if tag_words:
            tag_words = "{0}-{1}".format(n, tag_words)
        else:
            tag_words = n
        n = 1

    r = requests.get("http://{0}.tumblr.com/".format(author))
    if 200 <= r.status_code < 300:
        pr = r.url.split("://")[0]
        if tag_words:
            if tag_words[0] == "#" and len(tag_words) > 1:
                f = feedparser.parse("{0}://{1}.tumblr.com/tagged/{2}/rss".format(pr, author, tag_words[1:]))
            else:
                f = feedparser.parse("{0}://{1}.tumblr.com/search/{2}/rss".format(pr, author, tag_words))
        else:
            f = feedparser.parse("{0}://{1}.tumblr.com/rss".format(pr, author))

        f_max = 10 if len(f.entries) >= 10 else len(f.entries)
        if n > f_max:
            n = f_max
        elif n < 1:
            n = 1

        for num in range(n - 1, -1, -1):
            await client.say(f.entries[num].link)


@client.command(pass_context=True)
async def gh(ctx, repo="darkreader/darkreader", amount=3):
    """GitHub commits."""

    f = feedparser.parse("https://github.com/{0}/commits/master.atom".format(repo))

    if f.entries:
        n = amount
        f_max = 10 if len(f.entries) >= 10 else len(f.entries)
        if n > f_max:
            n = f_max
        elif n < 1:
            n = 1

        for num in range(n - 1, -1, -1):
            entry = f.entries[num]

            desc = ""
            raw_content = BeautifulSoup(entry.content[0]["value"], "html.parser").text
            content_parts = raw_content.split("\n")

            if len(content_parts) > 1:
                content_parts.remove(content_parts[0])
                if content_parts[0] == "":
                    content_parts.remove("")
                desc = "\n".join(content_parts)

            m = re.findall("#(\d+)", raw_content)
            if m:
                pulls = []
                for i in range(0, len(m)):
                    pulls.append("[#{0}](https://github.com/darkreader/darkreader/pull/{0})".format(m[i]))
                pulls_str = ", ".join(pulls)
                if desc:
                    desc = "{0}\n\n{1}".format(pulls_str, desc)
                else:
                    desc = pulls_str

            title = entry.title
            m = re.search("(.*) \(#(\d+)\)", raw_content)
            if m:
                title = m[1]

            embed = discord.Embed(
                title=title,
                url=entry.link,
                description=desc,
                timestamp=datetime.datetime.fromtimestamp(time.mktime(entry.updated_parsed))
            )
            embed.set_footer(
                text=entry.author,
                icon_url=entry.media_thumbnail[0]["url"]
            )

            await client.say(embed=embed)


@client.command(pass_context=True)
async def cr(ctx):
    """Currency checking."""

    await client.send_typing(ctx.message.channel)

    currency = []
    soup = req_soup("http://www.profinance.ru/chart/usdrub/")
    if soup:
        usd = soup.select("table.stat.news")[0].find("a", href="/chart/usdrub/").find_parent("td").find_next_sibling("td").text
        eur = soup.select("table.stat.news")[0].find("a", href="/chart/eurrub/").find_parent("td").find_next_sibling("td").text
        if usd:
            currency.append("\💵 {0}₽".format(round2(usd)))
        if eur:
            currency.append("\💶 {0}₽".format(round2(eur)))

    r = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD")
    if 200 <= r.status_code < 300:
        api_data = r.json()
        btc = api_data["BTC"]["USD"]
        if btc:
            currency.append("\🔶 ${0}".format(round2(btc)))
        eth = api_data["ETH"]["USD"]
        if btc:
            currency.append("\🔷 ${0}".format(round2(eth)))

    if currency:
        embed = discord.Embed(
            description="\n".join(currency)
        )
        embed.set_author(
            name="Currency now"
        )

        link = "http://j1.profinance.ru/delta/prochart?type=USDRUB&amount=300&chart_height=300&chart_width=400&grtype=6&tictype=9&iId=5"
        r = requests.get(link, headers=HEADERS)
        if 200 <= r.status_code < 300:
            image = Image.open(io.BytesIO(r.content))

            width = image.size[0]
            height = image.size[1]
            pix = image.convert('RGB')
            draw = ImageDraw.Draw(pix)

            for i in range(width):
                for j in range(height):
                    a, b, c = pix.getpixel((i, j))
                    draw.point((i, j), (255 - a, 255 - b, 255 - c))

            pix = pix.convert('RGBA')
            arr = np.array(np.asarray(pix).astype('float'))
            pix = Image.fromarray(shift_hue(arr, 0.57).astype('uint8'), 'RGBA')

            output_buffer = io.BytesIO()
            pix.save(output_buffer, "gif")
            output_buffer.seek(0)

            embed.set_image(url="attachment://chart.png")
            await client.http.send_file(
                ctx.message.channel.id,
                output_buffer,
                filename="chart.png",
                embed=embed.to_dict()
            )
        else:
            await client.say(embed=embed)


client.run(os.environ.get("TOKEN", None))
