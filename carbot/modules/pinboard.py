import discord
import sqlite3
import car


class PinBoard(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot=bot,
            global_category="Pinboard"
        )
        self.reacted_msgs = {}

    def create_pinboard(self, guild_id):
        # TODO: don't call this every update
        cur = self.bot.conn.cursor()
        cur.execute(f'''
                    CREATE TABLE IF NOT EXISTS pinboards_{guild_id}
                    (emoji TEXT PRIMARY KEY, channel INTEGER,
                    required_reactions INTEGER, required_role INTEGER)
                    ''')

    def query_emoji(self, guild_id, emoji):
        cur = self.bot.conn.cursor()
        try:
            cur.execute(f'SELECT * FROM pinboards_{guild_id} WHERE emoji = ?',
                    (emoji,))
        except sqlite3.OperationalError:
            raise IndexError

        fetch = cur.fetchone()
        if fetch is None:
            raise IndexError

        return fetch

    def insert_pinboard(self, guild_id, emoji_id, channel_id,
                        required_amount=1, required_role_id=0):
        cur = self.bot.conn.cursor()
        self.create_pinboard(guild_id)
        cur.execute(f'INSERT INTO pinboards_{guild_id} VALUES(?, ?, ?, ?)',
                    (emoji_id, channel_id, required_amount, required_role_id))
        self.bot.conn.commit()

    def delete_pinboard(self, guild_id, emoji_id):
        cur = self.bot.conn.cursor()
        self.create_pinboard(guild_id)
        cur.execute(f'DELETE FROM pinboards_{guild_id} WHERE emoji = ?',
                    (emoji_id,))
        self.bot.conn.commit()

    def fetch_pinboards(self, guild_id):
        cur = self.bot.conn.cursor()
        self.create_pinboard(guild_id)
        cur.execute(f'SELECT * FROM pinboards_{guild_id}')

        fetch = cur.fetchall()
        if len(fetch) == 0:
            raise car.CommandError("No pinboards found! Add one with `pbadd`")

        return fetch

    @car.listener
    async def on_reaction_add(self, reaction, user):
        msg = reaction.message

        try:
            fetch = self.query_emoji(msg.guild.id, str(reaction))
        except IndexError:
            return

        if msg.id in self.reacted_msgs:
            m = self.reacted_msgs[msg.id]
            if not m.content.split(' ')[-1] == f"**x{reaction.count}**":
                await m.edit(
                    content=f"{m.content.split(' ')[0]} **x{reaction.count}**"
                )
            return

        if reaction.count < fetch[2]:
            return

        desc = (f"[[Jump]]({msg.jump_url}) {msg.author.mention} in"
                f"{msg.channel.mention}\n\n{msg.content}")
        if len(desc) > 1500:
            desc = desc[:1500] + " *(continued)*"

        e = car.embed(description=desc)
        if len(msg.attachments) > 0:
            e.set_image(url=msg.attachments[0].url)
            e.add_field(
                name="Attachments",
                value='\n'.join(f"[{a.filename}]({a.url})"
                                for a in msg.attachments)
            )

        e.set_author(
            name=f"{msg.author.name}#{msg.author.discriminator}",
            icon_url=msg.author.avatar_url
        )

        c = discord.utils.get(msg.guild.channels, id=fetch[1])
        m = await c.send(f"{reaction.emoji} **x{reaction.count}**", embed=e)
        self.reacted_msgs[msg.id] = m

    @car.command()
    @car.requires_permissions(manage_guild=True)
    async def pbadd(
        self, ctx,
        channel: car.to_text_channel(),
        emoji: "an emoji",
        required_amount: car.to_int(lower=1) = 1
    ):
        """
        Adds a pinboard
        """
        try:
            self.insert_pinboard(ctx.guild.id, emoji, channel.id, required_amount)
        except sqlite3.IntegrityError:
            raise car.CommandError(f"Another board already uses {emoji}!")

        e = car.embed(description=f"Pinboard {emoji} added!")
        await ctx.send(embed=e)

    @car.command(aliases=["pbdelete", "pbremove"])
    @car.requires_permissions(manage_guild=True)
    async def pbdel(
        self, ctx,
        emoji: "an emoji"
    ):
        """
        Removes a pinboard
        """
        self.delete_pinboard(ctx.guild.id, emoji)
        e = car.embed(description=f"Pinboard {emoji} deleted!")
        await ctx.send(embed=e)

    @car.command()
    async def pblist(self, ctx):
        """
        Lists all pinboards
        """
        fetch = self.fetch_pinboards(ctx.guild.id)
        boards = []
        for board in fetch:
            boards.append(f"{board[0]} (x{board[2]}) • <#{board[1]}>")

        e = car.embed(title="Pinboard List", description='\n'.join(boards))
        e.set_footer(text="React to a message with these emotes to pin them")
        await ctx.send(embed=e)

