import discord
import car
import math
import bs4


class Typing(car.Cog):
    def __init__(self, bot):
        super().__init__(bot=bot, global_category="Typing")
        cur = self.bot.conn.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS typing (
                        id INTEGER PRIMARY KEY,
                        text TEXT,
                        length INTEGER,
                        diff INTEGER,
                        pool INTEGER
                    )
                    ''')

    def get_excerpt(self, *, id_=None, length=None, diff=None, pool=None):
        if isinstance(diff, str):
            diff = {
                "easy": (0,140),
                "med": (140,170),
                "hard": (170,250),
                "wtf": (250, 1000000)
            }[diff]

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

    return round(total_points / words * math.log(len(text)))
