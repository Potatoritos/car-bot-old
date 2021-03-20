import discord
import car
import random

class TestModule(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Hidden")

    @car.command()
    async def test3(self, ctx, name):
        doc = self.bot.commands[name].help('c.', [])

        embed = discord.Embed(description=doc)

        await ctx.send(embed=embed)

    @car.command()
    async def test_message_conv(self, ctx, msg: car.to_message()):
        print(msg)
        print(msg.content)

    @car.command(aliases=['test4'])
    async def test2(
        self, ctx,
        arg1: "test 1",
        arg2: car.to_int(),
        arg3: "Optional!!!!!!" = None,
        *,
        kwarg1: car.to_int() // ("thing", "sdkfjsdlkf jsldkfjsdlk ") = None,
        kwarg2: "bong" = None
    ):
        await ctx.send("hello")

    @car.command()
    async def etest(
        self, ctx
    ):
        raise car.CommandError("bong")

    @car.command()
    async def mtest(self, ctx, arg1: car.to_member(prompt=False)):
        # print(arg1)
        # await ctx.send('\n'.join([f"{m[0]} ({m[1]})" for m in arg1]))
        await ctx.send(arg1)

    @car.command()
    async def mmtest(self, ctx, arg1: car.to_member(amount=5)):
        await ctx.send('\n'.join(f"{m[0]} ({m[1]})" for m in arg1))

    @car.command()
    async def itest(self, ctx, arg1: car.to_int()):
        await ctx.send(arg1)

