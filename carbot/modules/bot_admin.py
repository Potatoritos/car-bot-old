import car
import sys
import os


class BotAdmin(car.Cog):
    def __init__(self, bot):
        super().__init__(
            bot,
            global_checks=[car.bot_owner_only()],
            global_category="Hidden"
        )
        cur = self.bot.conn.cursor()
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS trusted
                    (id INTEGER PRIMARY KEY)
                    ''')
        self.trusted = set()
        cur.execute('SELECT * FROM trusted')
        fetch = cur.fetchall()
        for i in fetch:
            self.trusted.add(i[0])

    @car.command()
    async def shutdown(self, ctx):
        await self.bot.logout()
        sys.exit()

    @car.command()
    async def restart(self, ctx): # TODO: fix
        await self.bot.logout()
        os.execv(sys.argv[0], sys.argv)

    @car.command(aliases=['alm'])
    async def load_module(self, ctx, name):
        try:
            self.bot.load_module(name)
        except ModuleNotFoundError:
            raise car.CommandError("Module not found!", 0)

        await ctx.send("Module loaded!")

    @car.command(aliases=['aum'])
    async def unload_module(self, ctx, name):
        try:
            self.bot.unload_module(name)
        except KeyError:
            raise car.CommandError("Module not found!", 0)

        await ctx.send("Module unloaded!")

    @car.command(aliases=['arm'])
    async def reload_module(self, ctx, name):
        try:
            self.bot.reload_module(name)
        except KeyError:
            raise car.CommandError("Module not found!", 0)

        await ctx.send("Module reloaded!")

    @car.command()
    async def list_modules(self, ctx):
        m = '\n'.join(k for k, v in self.bot.modules.items())
        await ctx.send(f"```{m}```")

    @car.command()
    async def add_trusted(self, ctx, member: car.to_member()):
        cur = self.bot.conn.cursor()
        cur.execute('INSERT INTO trusted VALUES (?)', (member.id,))
        self.bot.conn.commit()
        self.trusted.add(member.id)
        await ctx.reply("added")

    @car.command()
    async def remove_trusted(self, ctx, member: car.to_member()):
        cur = self.bot.conn.cursor()
        cur.execute('DELETE FROM trusted WHERE id = ?', (member.id,))
        self.bot.conn.commit()
        self.trusted.remove(member.id)
        await ctx.reply("removed")

    @car.command()
    async def list_trusted(self, ctx):
        cur = self.bot.conn.cursor()
        cur.execute('SELECT * FROM trusted')
        fetch = cur.fetchall()
        if len(fetch) == 0:
            await ctx.reply("no trusted")
            return
        e = car.embed(description='\n'.join(f"<@{i[0]}>" for i in fetch))
        await ctx.reply(embed=e)

