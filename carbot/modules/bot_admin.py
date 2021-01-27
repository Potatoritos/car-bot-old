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

