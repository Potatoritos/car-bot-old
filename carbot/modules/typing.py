import discord
import car
import math
from bs4 import BeautifulSoup
import time
import asyncio
import requests
import random


class Typing(car.Cog):
    def __init__(self, bot):
        super().__init__(bot=bot, global_category="Typing")
        cur = self.bot.conn.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS excerpts (
                        id INTEGER PRIMARY KEY,
                        text TEXT,
                        length INTEGER,
                        diff INTEGER,
                        pool INTEGER
                    )
                    ''')

    # def get_excerpt(self, *, id_=None, length=None, diff=None, pool=None):
        # if isinstance(diff, str):
            # diff = {
                # "easy": (0,1400),
                # "med": (1400,1700),
                # "hard": (1700,2500),
                # "wtf": (2500, 1000000)
            # }[diff]

        # cur.execute('''
                    # SELECT * FROM typing WHERE 
                    # ''')

    @car.command(aliases=["typingtest"])
    async def wpm(self, ctx):
        """
        Typing test
        """
        # TODO: add difficulty / length options
        cur = self.bot.conn.cursor()
        cur.execute('''
                    SELECT * FROM excerpts
                    WHERE diff BETWEEN 1300 AND 1700
                    AND length BETWEEN 150 AND 450
                    ''')
        fetch = cur.fetchall()
        excerpt = fetch[random.randint(0, len(fetch))]

        text = excerpt[1]
        diff = excerpt[3]

        await ctx.reply(f"```{car.zwsp(text, 'aei')}```")
        start = time.monotonic()
 
        try:
            msg = await self.bot.wait_for(
                "message",
                timeout = 300,
                check=lambda m: m.author == ctx.author \
                    and m.channel == ctx.channel
            )
        except asyncio.Timeouterror:
            raise car.CommandError("You took too long to complete this test!")

        # check for ZWSP
        if '​' in msg.content:
            await ctx.reply(":rotating_light: Copy and paste detected!")
            return

        # account for human reaction time
        elapsed = time.monotonic() - start - 0.4

        wpm = len(text.split(' ')) / elapsed * 60
        cpm = len(text) / elapsed * 60
        acc = 1 - car.edit_dist(text, msg.content) / len(text)

        e = car.embed(description=(
            f"`WPM` **{round(wpm * acc**3)}** *({round(wpm)})*\n"
            f"`CPM` **{round(cpm * acc**3)}** *({round(cpm)})*\n"
            f"`Acc` **{round(acc * 100, 1)}%**"
        ))
        e.set_author(name="Test Results",
            icon_url=ctx.author.avatar_url)
        e.set_footer(text=f"Text Difficulty: {diff}")

        await ctx.reply(embed=e)

    @car.command(category="Hidden")
    async def td(self, ctx, text):
        await ctx.send(typing_diff(text))

    @car.command(category="Hidden")
    @car.bot_owner_only()
    async def load_typeracer_excerpts(self, ctx):
        """
        retrieves typeracer.com texts
        """
        r = requests.get("http://typeracerdata.com/texts?texts=full")
        soup = BeautifulSoup(r.content, "html.parser")
        rows = soup.find_all("tr")
        cur = self.bot.conn.cursor()
        for i in range(1, len(rows)):
            text = rows[i].find_all("td")[2].find("a").decode_contents()
            cur.execute(
                "INSERT INTO excerpts VALUES(NULL, ?, ?, ?, 1)",
                (text, len(text), typing_diff(text))
            )
        self.bot.conn.commit()
        await ctx.send("done")

def is_shifted(char):
    return char.isupper() or char in '~!@#$%^&*()_+{}|:"<>?'

def typing_diff(text):
    current_points = 0
    total_points = 0
    words = 0

    text = f"  {text} "

    for i in range(2, len(text)):
        if text[i] == ' ':
            total_points += current_points**2
            current_points = 0
            words += 1
            continue

        current_points += 1 \
            + (is_shifted(text[i]) != is_shifted(text[i-1])) \
            + 0.25 * text[i].isdigit() \
            + 0.3 * (not text[i].isdigit() and not text[i].isalpha()) \
            + 0.5 * (text[i] == text[i-1] != text[i-2])

    return round(total_points*10 / words * math.log(len(text)))
